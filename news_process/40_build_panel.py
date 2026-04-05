"""
40_build_panel.py - Bank-Year 面板数据构建
==========================================

将篇章级新闻情感分析数据(23_bert_tone.parquet)转化为 **Bank-Year 面板数据**,
遵循 Tetlock et al. (2008, JF) 范式, 为 Stata 回归提供出版就绪数据集。

核心设计原则 - 先分后合(Disaggregate-then-Aggregate):
  情感指标不在篇章级预先综合, 而是在 Bank-Year 聚合阶段对每个模型/词典
  分别聚合, 最后在面板层级计算综合指标。

聚合指标设计:
  - tone_mean:       篇章级情感的简单均值 (EW)
  - tone_weighted:   提及密度加权均值 (VW, Hassan et al., 2019, QJE)
  - tone_mw:         媒体权威性加权均值 (MW, Holzman et al., 2023, TAR)
  - coverage_ratio:  篇数覆盖率 = 有效篇数 / 总篇数
  - article_count:   Bank-Year 下的总文章数
  - _tech / _app:    按 fintech_category 分组的分类情感均值
                     (底层技术 vs. 应用场景异质性分析)
  - fintech_exposure: ln_coverage × tone_std 复合指标
                     (Dim et al., 2024 NarrativeExposure 概念迁移)
  - _z 后缀列:       年度截面 z-score 标准化 (Fama-MacBeth 1973)

输入:
  data_processed/23_bert_tone.parquet

输出:
  data_processed/40_panel_yearly.parquet      (年度平衡面板)
  data_processed/40_panel_yearly.dta          (Stata 格式)
  data_processed/40_article_bank_level.parquet (展开后文章-银行级数据)
"""

import os
import re
import sys
import json
import time
import warnings

import numpy as np
import pandas as pd

from utils.helpers import (
    load_config, setup_logging, log_stage_summary, save_dataset
)

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "40_build_panel"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 输出路径
OUTPUT_DIR = CONFIG["paths"]["output_dir"]
FILENAMES = CONFIG.get("filenames", {})
PANEL_CFG = CONFIG.get("panel_building", {})

# LLM 模型 short_name 列表(从 tone_llm_processing.models 读取)
# 这些名称用于定位阶段 21 输出中各模型对应的情感结果列
_llm_cfg = CONFIG.get('tone_llm_processing', {}).get('models', [])
LLM_MODELS = [m['short_name'] for m in _llm_cfg] if _llm_cfg else ['gpt5nano', 'gemini3', 'claude4h']

# 词典名列表 — 对应阶段 22 中的五本中文金融情感词典
DICT_NAMES = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

# BERT 模型 short_name 列表与分类数（从 sentiment_analysis.tone_berts.models 读取）
_bert_cfg = CONFIG.get('sentiment_analysis', {}).get('tone_berts', {}).get('models', [])
BERT_MODELS = [m['short_name'] for m in _bert_cfg] if _bert_cfg else ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']

# 三分类模型（有 _中性 列）
THREE_CLASS_MODELS = set()
for m in _bert_cfg:
    lm = m.get('label_map', {})
    if '中性' in lm.values():
        THREE_CLASS_MODELS.add(m['short_name'])
if not THREE_CLASS_MODELS:
    THREE_CLASS_MODELS = {'finbert_cn', 'fin_sent_zh', 'hw2942'}


# ============================================================================
# 2. 情感编码函数
# 将三分类中文标签映射为数值, 便于 Stata 回归使用:
#   正面 -> +1, 中性 -> 0, 负面 -> -1
# ============================================================================

SENTIMENT_MAP = {'正面': 1, '中性': 0, '负面': -1}


def encode_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """篇章级情感数值编码：离散 + 连续（双轨）。"""
    logger.info("=" * 60)
    logger.info("步骤 2: 篇章级情感数值编码（双轨）")
    logger.info("=" * 60)

    encoded_cols = []
    for track in ['_full', '_ctx']:
        # --- LLM 投票结果 离散编码 ---
        df[f'llm_vote_score{track}'] = df[f'llm_sentiment{track}'].map(SENTIMENT_MAP).fillna(0).astype(int)
        df[f'is_positive{track}'] = (df[f'llm_vote_score{track}'] == 1).astype(int)
        df[f'is_negative{track}'] = (df[f'llm_vote_score{track}'] == -1).astype(int)
        df[f'is_neutral{track}'] = (df[f'llm_vote_score{track}'] == 0).astype(int)

        # --- LLM 投票结果 连续编码 ---
        df[f'llm_vote_cont{track}'] = df[f'llm_vote_score{track}'] * df[f'llm_agreement_rate{track}'].fillna(0)

        # --- LLM 逐模型 离散 + 连续编码 ---
        for short in LLM_MODELS:
            sent_col = f'{short}_sentiment{track}'
            conf_col = f'{short}_sentiment_confidence{track}'
            if sent_col in df.columns:
                df[f'{short}_score{track}'] = df[sent_col].map(SENTIMENT_MAP).fillna(0).astype(int)
                if conf_col in df.columns:
                    df[f'{short}_cont{track}'] = df[f'{short}_score{track}'] * df[conf_col].fillna(0)
                else:
                    df[f'{short}_cont{track}'] = df[f'{short}_score{track}'].astype(float)

        encoded_cols.extend([
            f'llm_vote_score{track}', f'is_positive{track}', f'is_negative{track}',
            f'is_neutral{track}', f'llm_vote_cont{track}'
        ])
        for short in LLM_MODELS:
            encoded_cols.extend([f'{short}_score{track}', f'{short}_cont{track}'])

    # --- 词典法 & BERT: 直接使用上游连续值, 无需额外编码 ---

    logger.info(f"  生成编码列: {len(encoded_cols)} 个")
    logger.info(f"  离散映射: 正面=1, 中性=0, 负面=-1")
    logger.info(f"  连续编码: direction × confidence ∈ [-1, +1]")
    return df


# explode_banks 函数已移除 — 展开逻辑已迁移至 11_news_bank.py（Phase 1 提早展开）
# 数据抵达此阶段时已包含 target_bank、co_mentioned_banks 等列


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


# ============================================================================
# 3c. 媒体权威性加权 (Holzman, Miller & Twedt 2023, TAR)
# ============================================================================

def compute_media_authority_weights(df: pd.DataFrame) -> pd.DataFrame:
    """步骤 3c: 媒体权威性加权。

    学术依据:
      Holzman, E.R., Miller, B.P. & Twedt, B.J. (2023).
      "Curbing Enthusiasm: Media Sentiment and the Disciplining Role
      of Quarterly Earnings Announcements."
      The Accounting Review, 98(7), 315-345. DOI: 10.2308/TAR-2020-0104
      → Appendix A: Outlet Impact Media Sent 加权方法

    该论文通过滚动回归估计每家媒体对股票周转率的边际贡献,
    然后按排名百分位加权。本项目使用 media_weights.json 中的
    静态权威性评分 (10-100) 作为简化替代。

    匹配策略: 精确匹配 → 去括号归一化匹配 → 默认权重。
    归一化: raw_weight / mean(raw_weight), 使量级 ≈ 等权版。

    Args:
        df: 篇章级 DataFrame, 须含 '媒体(中文)' 列。

    Returns:
        df: 附加 'media_authority_weight' 列的 DataFrame。
    """
    logger.info("=" * 60)
    logger.info("步骤 3c: 媒体权威性加权 (Holzman et al. 2023, TAR)")
    logger.info("=" * 60)

    # ── 加载 media_weights.json ──
    weights_path = CONFIG['paths'].get('media_weights_file', '')
    if not os.path.exists(weights_path):
        logger.warning(f"  media_weights_file 不存在: {weights_path}, 全部使用默认权重")
        df['media_authority_weight'] = 1.0
        return df

    with open(weights_path, 'r', encoding='utf-8') as f:
        raw_weights = json.load(f)
    # 过滤注释键
    media_weights = {k: v for k, v in raw_weights.items()
                     if not k.startswith('//')}
    logger.info(f"  已加载 {len(media_weights)} 条媒体权重")

    # 默认权重: 从 media_weights.json 的 "default" 键读取
    # 与 38_media_diversity.py 的 media_weights.get("default", 10) 一致
    default_weight = media_weights.get('default', 10)
    logger.info(f"  未评级媒体默认权重: {default_weight}")

    # ── 双层匹配 ──
    def _normalize_media_name(name: str) -> str:
        """去除括号后缀: '扬子晚报(数字报)' → '扬子晚报'。"""
        return re.sub(r'[（(][^)）]*[)）]', '', str(name)).strip()

    exact_count = 0
    fuzzy_count = 0
    default_count = 0
    weights_assigned = []

    for idx, name in df['媒体(中文)'].items():
        name_str = str(name).strip()
        if name_str in media_weights:
            w = media_weights[name_str]
            exact_count += 1
        else:
            norm_name = _normalize_media_name(name_str)
            if norm_name in media_weights:
                w = media_weights[norm_name]
                fuzzy_count += 1
            else:
                w = default_weight
                default_count += 1
        weights_assigned.append(w)

    raw_series = pd.Series(weights_assigned, index=df.index, dtype=float)

    # ── 均值归一化 ──
    raw_mean = raw_series.mean()
    if raw_mean > 0:
        df['media_authority_weight'] = raw_series / raw_mean
    else:
        df['media_authority_weight'] = 1.0

    # ── 诊断日志 ──
    total = len(df)
    logger.info(f"  匹配诊断: 精确={exact_count} ({exact_count/total:.1%}), "
                f"归一化={fuzzy_count} ({fuzzy_count/total:.1%}), "
                f"默认={default_count} ({default_count/total:.1%})")
    logger.info(f"  原始权重: mean={raw_series.mean():.1f}, "
                f"min={raw_series.min():.0f}, max={raw_series.max():.0f}")
    logger.info(f"  归一化后: mean={df['media_authority_weight'].mean():.4f}, "
                f"std={df['media_authority_weight'].std():.4f}")

    return df


# ============================================================================
# 4. 时间解析
# ============================================================================

def parse_time(df: pd.DataFrame) -> pd.DataFrame:
    """从日期列提取年份。"""
    logger.info("=" * 60)
    logger.info("步骤 4: 时间解析")
    logger.info("=" * 60)

    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df['year'] = df['日期'].dt.year

    # 过滤无效日期
    invalid_dates = df['year'].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"  发现 {invalid_dates:,} 条无效日期, 已过滤")
        df = df.dropna(subset=['year']).reset_index(drop=True)

    df['year'] = df['year'].astype(int)

    year_range = f"{df['year'].min()} - {df['year'].max()}"
    logger.info(f"  时间跨度: {year_range}")
    logger.info(f"  年份分布: {df['year'].value_counts().sort_index().to_dict()}")
    return df


# ============================================================================
# 5. Bank-Year 聚合
# ============================================================================

def build_aggregation_dict() -> dict:
    """构建 GroupBy 聚合字典(双轨)。

    聚合策略遵循 Tetlock et al. (2008, JF) 范式:
      - mean: Bank-Year 均值(核心情感指标)
      - sum:  Bank-Year 总和(加权指标的分子)
      - std:  Bank-Year 标准差(情感分散度, 反映信息环境不确定性)
      - count: 新闻覆盖量

    双轨(_full + _ctx)确保全文和上下文片段两种输入分别聚合,
    供下游消融研究和稳健性检验使用。
    """
    agg = {}

    for track in ['_full', '_ctx']:
        # --- A. LLM 逐模型 ---
        for short in LLM_MODELS:
            agg[f'{short}_tone{track}'] = (f'{short}_score{track}', 'mean')
            agg[f'{short}_tone_sum{track}'] = (f'{short}_score{track}', 'sum')
            agg[f'{short}_cont_mean{track}'] = (f'{short}_cont{track}', 'mean')
            agg[f'{short}_cont_sum{track}'] = (f'{short}_cont{track}', 'sum')
            agg[f'{short}_tone_std{track}'] = (f'{short}_score{track}', 'std')

        # --- B. LLM 投票结果 ---
        agg[f'llm_vote_tone{track}'] = (f'llm_vote_score{track}', 'mean')
        agg[f'llm_vote_tone_sum{track}'] = (f'llm_vote_score{track}', 'sum')
        agg[f'llm_vote_tone_std{track}'] = (f'llm_vote_score{track}', 'std')
        agg[f'pos_frac{track}'] = (f'is_positive{track}', 'mean')
        agg[f'neg_frac{track}'] = (f'is_negative{track}', 'mean')
        agg[f'pos_count{track}'] = (f'is_positive{track}', 'sum')
        agg[f'neg_count{track}'] = (f'is_negative{track}', 'sum')
        agg[f'llm_vote_cont{track}'] = (f'llm_vote_cont{track}', 'mean')
        agg[f'llm_vote_cont_sum{track}'] = (f'llm_vote_cont{track}', 'sum')

        # --- C. 词典法 ---
        for d in DICT_NAMES:
            agg[f'{d}_tone{track}'] = (f'{d}_score{track}', 'mean')
            agg[f'{d}_tone_sum{track}'] = (f'{d}_score{track}', 'sum')
            agg[f'{d}_tone_std{track}'] = (f'{d}_score{track}', 'std')

        # --- C2. 词典法 IDF 加权稳健性检验 (Gentzkow, Kelly & Taddy 2019, JEL) ---
        for d in DICT_NAMES:
            agg[f'{d}_idf_tone{track}'] = (f'{d}_idf_score{track}', 'mean')
            agg[f'{d}_idf_tone_sum{track}'] = (f'{d}_idf_score{track}', 'sum')
            agg[f'{d}_idf_tone_std{track}'] = (f'{d}_idf_score{track}', 'std')

        # --- D. BERT 逐模型 ---
        for short in BERT_MODELS:
            agg[f'{short}_pos{track}'] = (f'{short}_正面{track}', 'mean')
            agg[f'{short}_pos_sum{track}'] = (f'{short}_正面{track}', 'sum')
            agg[f'{short}_neg{track}'] = (f'{short}_负面{track}', 'mean')
            agg[f'{short}_neg_sum{track}'] = (f'{short}_负面{track}', 'sum')
            agg[f'{short}_pos_std{track}'] = (f'{short}_正面{track}', 'std')
            if short in THREE_CLASS_MODELS:
                agg[f'{short}_neu{track}'] = (f'{short}_中性{track}', 'mean')
                agg[f'{short}_neu_sum{track}'] = (f'{short}_中性{track}', 'sum')

        # --- G. 前瞻性陈述 (Li 2010, JAR) ---
        agg[f'avg_fl_ratio{track}'] = (f'forward_looking_ratio{track}', 'mean')
        agg[f'avg_fl_ratio_std{track}'] = (f'forward_looking_ratio{track}', 'std')
        agg[f'sum_fl_count{track}'] = (f'forward_looking_count{track}', 'sum')

        # --- H. 文本可读性控制变量 (Loughran & McDonald 2014, JF) ---
        agg[f'avg_sent_len{track}'] = (f'avg_sentence_len{track}', 'mean')
        agg[f'avg_ttr{track}'] = (f'type_token_ratio{track}', 'mean')
        agg[f'avg_cpw{track}'] = (f'char_per_word{track}', 'mean')

        # --- I. 正/负面词频分离 (Berger, Kim & Ma 2024, CAR;
        #        Loughran & McDonald 2011, JF) ---
        agg[f'avg_pos_ratio{track}'] = (f'pos_ratio{track}', 'mean')
        agg[f'avg_neg_ratio{track}'] = (f'neg_ratio{track}', 'mean')
        agg[f'avg_pos_ratio_std{track}'] = (f'pos_ratio{track}', 'std')
        agg[f'avg_neg_ratio_std{track}'] = (f'neg_ratio{track}', 'std')

        # --- I2. 计数型情感指标 MSENT (He et al. 2024, IRFA;
        #         Tetlock 2007, JF) ---
        agg[f'avg_msent{track}'] = (f'msent_score{track}', 'mean')
        agg[f'avg_msent_std{track}'] = (f'msent_score{track}', 'std')
        agg[f'msent_sum{track}'] = (f'msent_score{track}', 'sum')

    # --- E. 新闻覆盖量 & 稳健性辅助（无需双轨） ---
    agg['n_articles'] = ('llm_vote_score_full', 'count')
    agg['headline_frac'] = ('in_title', 'mean')
    agg['multi_bank_frac'] = ('is_multi_bank', 'mean')
    agg['avg_bank_count'] = ('bank_count', 'mean')
    agg['max_bank_count'] = ('bank_count', 'max')
    agg['avg_agreement_rate_full'] = ('llm_agreement_rate_full', 'mean')
    agg['avg_agreement_rate_ctx'] = ('llm_agreement_rate_ctx', 'mean')

    # --- F. Value-weighted 辅助列 (Hassan et al. 2019, QJE; Sautner et al. 2023, JF) ---
    agg['sum_mention_density'] = ('mention_density', 'sum')
    agg['sum_doc_length'] = ('doc_length', 'sum')
    agg['avg_doc_length'] = ('doc_length', 'mean')
    agg['sum_target_mentions'] = ('target_bank_mention_count', 'sum')
    for track in ['_full', '_ctx']:
        agg[f'llm_vote_score_w_sum{track}'] = (f'llm_vote_score_w{track}', 'sum')
        agg[f'llm_vote_cont_w_sum{track}'] = (f'llm_vote_cont_w{track}', 'sum')
        agg[f'pos_count_vw{track}'] = (f'is_positive_w{track}', 'sum')
        agg[f'neg_count_vw{track}'] = (f'is_negative_w{track}', 'sum')
        for short in LLM_MODELS:
            agg[f'{short}_score_w_sum{track}'] = (f'{short}_score_w{track}', 'sum')
            agg[f'{short}_cont_w_sum{track}'] = (f'{short}_cont_w{track}', 'sum')
        for d in DICT_NAMES:
            agg[f'{d}_score_w_sum{track}'] = (f'{d}_score_w{track}', 'sum')
        # --- F2. IDF VW 聚合 (Gentzkow, Kelly & Taddy 2019, JEL) ---
        for d in DICT_NAMES:
            agg[f'{d}_idf_score_w_sum{track}'] = (f'{d}_idf_score_w{track}', 'sum')
        for b in BERT_MODELS:
            agg[f'{b}_正面_w_sum{track}'] = (f'{b}_正面_w{track}', 'sum')
            agg[f'{b}_负面_w_sum{track}'] = (f'{b}_负面_w{track}', 'sum')

    # --- F3. 媒体权威性加权聚合 (Holzman et al. 2023, TAR) ---
    agg['sum_media_authority_weight'] = ('media_authority_weight', 'sum')
    for track in ['_full', '_ctx']:
        agg[f'llm_vote_score_mw_sum{track}'] = (f'llm_vote_score_mw{track}', 'sum')
        agg[f'llm_vote_cont_mw_sum{track}'] = (f'llm_vote_cont_mw{track}', 'sum')
        for short in LLM_MODELS:
            agg[f'{short}_score_mw_sum{track}'] = (f'{short}_score_mw{track}', 'sum')
            agg[f'{short}_cont_mw_sum{track}'] = (f'{short}_cont_mw{track}', 'sum')
        for d in DICT_NAMES:
            agg[f'{d}_score_mw_sum{track}'] = (f'{d}_score_mw{track}', 'sum')
            agg[f'{d}_idf_score_mw_sum{track}'] = (f'{d}_idf_score_mw{track}', 'sum')
        for b in BERT_MODELS:
            agg[f'{b}_正面_mw_sum{track}'] = (f'{b}_正面_mw{track}', 'sum')
            agg[f'{b}_负面_mw_sum{track}'] = (f'{b}_负面_mw{track}', 'sum')

    return agg


def aggregate_panel(df: pd.DataFrame) -> pd.DataFrame:
    """按 (target_bank, year) 聚合生成面板。

    核心输出:
      - n_articles: Bank-Year 下的新闻篇数 (Fang & Peress 2009, JF)
      - media_breadth: log(1 + 不同媒体来源数)(信息环境指标)
      - VW Tone: 提及密度加权情感 (Hassan et al. 2019, QJE)
      - _tech / _app 分类指标: 按 fintech_category 分组的情感均值
    """
    logger.info("=" * 60)
    logger.info("步骤 5: Bank-Year 聚合")
    logger.info("=" * 60)

    agg_dict = build_aggregation_dict()

    # 验证源列存在性, 过滤不存在的聚合
    valid_agg = {}
    missing_cols = []
    for out_col, (src_col, func) in agg_dict.items():
        if src_col in df.columns:
            valid_agg[out_col] = (src_col, func)
        else:
            missing_cols.append(f"{out_col} <- {src_col}")

    if missing_cols:
        logger.warning(f"  以下聚合因源列缺失而跳过 ({len(missing_cols)}):")
        for m in missing_cols[:10]:
            logger.warning(f"    - {m}")
        if len(missing_cols) > 10:
            logger.warning(f"    ... 及其余 {len(missing_cols) - 10} 个")

    # 执行聚合
    panel = df.groupby(['target_bank', 'year']).agg(**valid_agg).reset_index()

    # --- 媒体广度 ---
    if '媒体(中文)' in df.columns:
        media_breadth = df.groupby(['target_bank', 'year'])['媒体(中文)'].nunique().reset_index()
        media_breadth.columns = ['target_bank', 'year', '_media_nunique']
        panel = panel.merge(media_breadth, on=['target_bank', 'year'], how='left')
        panel['media_breadth'] = np.log1p(panel['_media_nunique'].fillna(0))
        panel.drop(columns=['_media_nunique'], inplace=True)
    else:
        logger.warning("  列 '媒体(中文)' 不存在, media_breadth 将为 NaN")
        panel['media_breadth'] = np.nan

    # --- 按 fintech_category 分组聚合（底层技术 / 应用场景） ---
    if 'fintech_category' in df.columns:
        # 防御性校验：检查非预期值
        valid_cats = {'底层技术', '应用场景'}
        actual_cats = set(df['fintech_category'].dropna().unique())
        unexpected = actual_cats - valid_cats
        if unexpected:
            logger.warning(f"  fintech_category 含非预期值: {unexpected}，这些文章将不计入分类聚合")

        cat_mapping = [('底层技术', '_tech'), ('应用场景', '_app')]

        for cat_label, suffix in cat_mapping:
            df_cat = df[df['fintech_category'] == cat_label]
            if df_cat.empty:
                logger.warning(f"  分类 '{cat_label}' 无文章，跳过 {suffix} 聚合")
                panel[f'n_articles{suffix}'] = 0
                continue

            # 构建分类聚合字典（仅 mean，不含 sum/std/VW）
            cat_agg = {}
            cat_agg[f'n_articles{suffix}'] = ('llm_vote_score_full', 'count')

            for track in ['_full', '_ctx']:
                # A. LLM 逐模型（离散 + 连续）
                for short in LLM_MODELS:
                    src_score = f'{short}_score{track}'
                    src_cont = f'{short}_cont{track}'
                    if src_score in df_cat.columns:
                        cat_agg[f'{short}_tone{suffix}{track}'] = (src_score, 'mean')
                    if src_cont in df_cat.columns:
                        cat_agg[f'{short}_cont_mean{suffix}{track}'] = (src_cont, 'mean')

                # B. LLM 投票
                src_vote = f'llm_vote_score{track}'
                src_vcont = f'llm_vote_cont{track}'
                if src_vote in df_cat.columns:
                    cat_agg[f'llm_vote_tone{suffix}{track}'] = (src_vote, 'mean')
                if src_vcont in df_cat.columns:
                    cat_agg[f'llm_vote_cont{suffix}{track}'] = (src_vcont, 'mean')

                # C. 词典法
                for d in DICT_NAMES:
                    src_d = f'{d}_score{track}'
                    if src_d in df_cat.columns:
                        cat_agg[f'{d}_tone{suffix}{track}'] = (src_d, 'mean')

                # C2. 词典法 IDF
                for d in DICT_NAMES:
                    src_idf = f'{d}_idf_score{track}'
                    if src_idf in df_cat.columns:
                        cat_agg[f'{d}_idf_tone{suffix}{track}'] = (src_idf, 'mean')

                # D. BERT
                for short in BERT_MODELS:
                    src_pos = f'{short}_正面{track}'
                    src_neg = f'{short}_负面{track}'
                    if src_pos in df_cat.columns:
                        cat_agg[f'{short}_pos{suffix}{track}'] = (src_pos, 'mean')
                    if src_neg in df_cat.columns:
                        cat_agg[f'{short}_neg{suffix}{track}'] = (src_neg, 'mean')
                    if short in THREE_CLASS_MODELS:
                        src_neu = f'{short}_中性{track}'
                        if src_neu in df_cat.columns:
                            cat_agg[f'{short}_neu{suffix}{track}'] = (src_neu, 'mean')

            # 单次 groupby + 单次 merge
            cat_panel = df_cat.groupby(['target_bank', 'year']).agg(**cat_agg).reset_index()
            panel = panel.merge(cat_panel, on=['target_bank', 'year'], how='left')
            logger.info(f"  分类 '{cat_label}' 聚合完成: {len(cat_panel):,} 个 Bank-Year, "
                        f"{len(cat_agg)} 个指标")

        # 分类计数列填充（merge 后可能产生 NaN）
        for suffix in ['_tech', '_app']:
            col = f'n_articles{suffix}'
            if col in panel.columns:
                panel[col] = panel[col].fillna(0).astype(int)

        # tech_frac / app_frac
        panel['tech_frac'] = np.where(
            panel['n_articles'] > 0,
            panel['n_articles_tech'] / panel['n_articles'],
            np.nan
        )
        panel['app_frac'] = np.where(
            panel['n_articles'] > 0,
            panel['n_articles_app'] / panel['n_articles'],
            np.nan
        )

        # avg_category_confidence
        if 'category_confidence' in df.columns:
            conf = df.groupby(['target_bank', 'year'])['category_confidence'].mean().reset_index()
            conf.columns = ['target_bank', 'year', 'avg_category_confidence']
            panel = panel.merge(conf, on=['target_bank', 'year'], how='left')
        else:
            panel['avg_category_confidence'] = np.nan

        # 恒等式校验
        if 'n_articles_tech' in panel.columns and 'n_articles_app' in panel.columns:
            has_news = panel['n_articles'] > 0
            identity_check = (panel.loc[has_news, 'n_articles'] ==
                              panel.loc[has_news, 'n_articles_tech'] + panel.loc[has_news, 'n_articles_app'])
            if identity_check.all():
                logger.info("  ✓ 恒等式校验通过: n_articles == n_articles_tech + n_articles_app")
            else:
                n_fail = (~identity_check).sum()
                logger.warning(f"  ✗ 恒等式校验失败: {n_fail} 行不满足 n_articles == n_articles_tech + n_articles_app")
    else:
        logger.info("  列 'fintech_category' 不存在, 分类聚合将跳过")
        panel['tech_frac'] = np.nan
        panel['app_frac'] = np.nan

    # 新闻覆盖量对数
    panel['ln_news_coverage'] = np.log1p(panel['n_articles'])

    # --- Value-weighted Tone 计算 (Hassan et al. 2019, QJE; 双轨) ---
    # 公式: VW_tone_i = Σ(mention_density_j × tone_j) / Σ(mention_density_j)
    # 其中 j 遍历 Bank i 在 Year t 下的所有文章。
    # 提及密度越高的文章对聚合情感的贡献越大,
    # 这反映了"银行作为核心主题的文章应有更大权重"的直觉。
    if 'sum_mention_density' in panel.columns:
        denom = panel['sum_mention_density'].replace(0, np.nan)
        for track in ['_full', '_ctx']:
            if f'llm_vote_score_w_sum{track}' in panel.columns:
                panel[f'llm_vote_tone_vw{track}'] = panel[f'llm_vote_score_w_sum{track}'] / denom
            if f'llm_vote_cont_w_sum{track}' in panel.columns:
                panel[f'llm_vote_cont_vw{track}'] = panel[f'llm_vote_cont_w_sum{track}'] / denom
            for short in LLM_MODELS:
                w_col = f'{short}_score_w_sum{track}'
                if w_col in panel.columns:
                    panel[f'{short}_tone_vw{track}'] = panel[w_col] / denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_w_sum{track}'
                if w_col in panel.columns:
                    panel[f'{d}_tone_vw{track}'] = panel[w_col] / denom
            # IDF VW Tone (Gentzkow, Kelly & Taddy 2019, JEL)
            for d in DICT_NAMES:
                w_col = f'{d}_idf_score_w_sum{track}'
                if w_col in panel.columns:
                    panel[f'{d}_idf_tone_vw{track}'] = panel[w_col] / denom
            for b in BERT_MODELS:
                w_pos = f'{b}_正面_w_sum{track}'
                w_neg = f'{b}_负面_w_sum{track}'
                if w_pos in panel.columns:
                    panel[f'{b}_pos_vw{track}'] = panel[w_pos] / denom
                if w_neg in panel.columns:
                    panel[f'{b}_neg_vw{track}'] = panel[w_neg] / denom
        logger.info(f"  已计算 Value-weighted Tone 指标（双轨）")

    # --- MW Tone (媒体权威性加权, Holzman et al. 2023, TAR) ---
    if 'sum_media_authority_weight' in panel.columns:
        mw_denom = panel['sum_media_authority_weight'].replace(0, np.nan)
        for track in ['_full', '_ctx']:
            if f'llm_vote_score_mw_sum{track}' in panel.columns:
                panel[f'llm_vote_tone_mw{track}'] = (
                    panel[f'llm_vote_score_mw_sum{track}'] / mw_denom)
            if f'llm_vote_cont_mw_sum{track}' in panel.columns:
                panel[f'llm_vote_cont_mw{track}'] = (
                    panel[f'llm_vote_cont_mw_sum{track}'] / mw_denom)
            for short in LLM_MODELS:
                w_col = f'{short}_score_mw_sum{track}'
                if w_col in panel.columns:
                    panel[f'{short}_tone_mw{track}'] = panel[w_col] / mw_denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_mw_sum{track}'
                if w_col in panel.columns:
                    panel[f'{d}_tone_mw{track}'] = panel[w_col] / mw_denom
                w_idf = f'{d}_idf_score_mw_sum{track}'
                if w_idf in panel.columns:
                    panel[f'{d}_idf_tone_mw{track}'] = panel[w_idf] / mw_denom
            for b in BERT_MODELS:
                for label, sfx in [('_正面', '_pos'), ('_负面', '_neg')]:
                    w_col = f'{b}{label}_mw_sum{track}'
                    if w_col in panel.columns:
                        panel[f'{b}{sfx}_mw{track}'] = panel[w_col] / mw_denom
        logger.info(f"  已计算 Media-Authority-weighted Tone 指标（双轨）")

    logger.info(f"  聚合后面板行数: {panel.shape[0]:,}")
    logger.info(f"  唯一银行数: {panel['target_bank'].nunique()}")
    logger.info(f"  年份范围: {panel['year'].min()} - {panel['year'].max()}")
    return panel


# ============================================================================
# 6. 面板平衡与缺失期填充
# ============================================================================

def balance_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """构建平衡面板: 银行 × 年份笛卡尔积 + 科学填充。

    填充策略:
      - 计数类(n_articles, n_articles_tech, n_articles_app): 填充为 0
      - 比例类(tech_frac, app_frac, avg_category_confidence): 保持 NaN
      - 情感类(所有 _tone, _pos, _neg 列): 保持 NaN
    """
    logger.info("=" * 60)
    logger.info("步骤 6: 面板平衡与缺失期填充 (Panel Balancing)")
    logger.info("=" * 60)

    rows_before = len(panel)

    all_banks = sorted(panel['target_bank'].unique())
    all_years = list(range(panel['year'].min(), panel['year'].max() + 1))

    full_index = pd.MultiIndex.from_product(
        [all_banks, all_years], names=['target_bank', 'year']
    )

    panel = panel.set_index(['target_bank', 'year']).reindex(full_index).reset_index()

    rows_after = len(panel)
    filled_count = rows_after - rows_before

    # --- 科学填充 ---
    # 填充为 0 的列: 计数类和流量类
    zero_fill_patterns = ['n_articles', 'ln_news_coverage', 'media_breadth']
    sum_cols = [c for c in panel.columns if c.endswith('_sum')]
    count_cols = ['pos_count', 'neg_count',
                  'pos_count_vw', 'neg_count_vw',
                  'sum_mention_density', 'sum_doc_length', 'sum_target_mentions',
                  'sum_fl_count_full', 'sum_fl_count_ctx',
                  'sum_media_authority_weight']
    zero_fill_cols = zero_fill_patterns + sum_cols + count_cols

    for col in zero_fill_cols:
        if col in panel.columns:
            panel[col] = panel[col].fillna(0)

    # --- 分类维度计数列填充为 0 ---
    # zero_fill_patterns 中的 'n_articles' 为精确匹配，不会捕获 n_articles_tech / n_articles_app
    for suffix in ['_tech', '_app']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # 其余 NaN 列保持不变（均值、比例、离散度等由 Stata 处理）
    # tech_frac / app_frac / avg_category_confidence: 零新闻行保持 NaN

    logger.info(f"  完全笛卡尔积: {len(all_banks)} 银行 × {len(all_years)} 年 = {rows_after:,} 行")
    logger.info(f"  原有观测值: {rows_before:,} 行")
    fill_pct = filled_count / rows_after if rows_after > 0 else 0
    logger.info(f"  填充的零新闻观测: {filled_count:,} 行 ({fill_pct:.1%})")

    return panel


# ============================================================================
# 6b. 金融科技公众注意力指数 (Bhojraj et al. 2025, §3.2)
# ============================================================================

# 小地理单元最低文章数阈值 (低于此值的 geo×year 不参与指数计算)
_ATTN_MIN_ARTICLES = 5


def compute_fintech_attention_index(panel: pd.DataFrame) -> pd.DataFrame:
    """构建金融科技公众注意力指数 — 三级地理维度。

    对标: Bhojraj, Guest, Wang & Yu (2025, §3.2, Eq. 1a)

    数据源:
      12_fintech_news_full.parquet — 全量银行新闻 (含 is_fintech_news 标记)。
      该文件为 article × bank 粒度。统一作为指数和权重的数据源，
      避免 df_exploded (仅含 fintech 文章) 导致的地理曝露偏差。

    去重策略:
      - 计算注意力指数 → 按 docid 去重到唯一文章级
      - 计算银行地理曝露权重 → 不去重 (每个 target_bank 行算一次曝露)

    NaN 语义:
      某 Bank-Year 的全部文章均缺失地理信息时，
      ft_attn_prov / ft_attn_city 为 NaN (不填充)。

    操作序列:
      在 balance_panel() 之后、compute_composite_indicators() 之前调用。

    Returns:
        panel: 附加 ft_attn_yr, ft_attn_prov, ft_attn_city 三列的面板。
    """
    full_path = os.path.join(OUTPUT_DIR, FILENAMES.get(
        'output_12_fintech_full', '12_fintech_news_full.parquet'))
    if not os.path.exists(full_path):
        logger.warning("  12_fintech_news_full.parquet 不存在, 跳过注意力指数")
        return panel

    logger.info("=" * 60)
    logger.info("步骤 6b: 金融科技公众注意力指数 (Bhojraj et al. 2025)")
    logger.info("=" * 60)

    # ── 加载 ──
    core_cols = ['docid', 'target_bank', '日期', 'is_fintech_news']
    geo_cols = ['国家地区/省份', '城市']
    # 仅加载 parquet 中实际存在的列 (地理列可选)
    import pyarrow.parquet as pq
    available = set(pq.read_schema(full_path).names)
    need_cols = [c for c in core_cols + geo_cols if c in available]
    missing_core = [c for c in core_cols if c not in available]
    if missing_core:
        logger.error(f"  12_fintech_news_full 缺少核心列: {missing_core}, 跳过")
        return panel
    missing_geo = [c for c in geo_cols if c not in available]
    if missing_geo:
        logger.warning(f"  12_fintech_news_full 缺少地理列: {missing_geo}, "
                       f"仅计算 Year-level 指数")
    df_all = pd.read_parquet(full_path, columns=need_cols)
    df_all['year'] = pd.to_datetime(df_all['日期'], errors='coerce').dt.year
    df_all = df_all.dropna(subset=['year'])
    df_all['year'] = df_all['year'].astype(int)
    logger.info(f"  加载: {len(df_all):,} 行 (article × bank)")

    # 标准化地理列
    _GEO_NAN_VALUES = frozenset({'', 'nan', 'None', '未知', 'NaN', '<NA>'})
    for col in ['国家地区/省份', '城市']:
        if col in df_all.columns:
            df_all[col] = (df_all[col].astype(str).str.strip()
                           .str.replace(r'\s+', '', regex=True))
            df_all.loc[df_all[col].isin(_GEO_NAN_VALUES), col] = np.nan

    # ── 按 docid 去重 → 唯一文章 (计算注意力指数) ──
    df_unique = df_all.drop_duplicates(subset=['docid'])
    logger.info(f"  唯一文章: {len(df_unique):,}")

    # ═══════════════════════════════════════════════════════
    # (A) Year-level 指数 (基准 / 稳健性参照)
    # ═══════════════════════════════════════════════════════
    yr_total = df_unique.groupby('year').size().rename('_total')
    yr_ft = (df_unique[df_unique['is_fintech_news'] == True]
             .groupby('year').size().rename('_ft'))
    idx_yr = pd.concat([yr_total, yr_ft], axis=1).fillna(0)
    idx_yr['ft_attn_yr'] = idx_yr['_ft'] / idx_yr['_total']
    idx_yr = idx_yr.reset_index()

    logger.info("  ─── Year-level ───")
    for _, r in idx_yr.iterrows():
        logger.info(f"    {int(r['year'])}: "
                     f"{int(r['_ft']):,}/{int(r['_total']):,} "
                     f"= {r['ft_attn_yr']:.4f}")

    # 保存中间数据
    _save_attn_index(idx_yr.rename(columns={'_total': 'total_articles',
                                             '_ft': 'fintech_articles'}),
                     '40_attn_index_year')

    panel = panel.merge(idx_yr[['year', 'ft_attn_yr']],
                        on='year', how='left')

    # ═══════════════════════════════════════════════════════
    # (B) Province × Year 指数
    # ═══════════════════════════════════════════════════════
    prov_col = '国家地区/省份'
    if prov_col in df_unique.columns:
        idx_prov = _build_geo_index(df_unique, prov_col, 'ft_attn_prov',
                                    min_articles=_ATTN_MIN_ARTICLES)
        # 保存中间数据
        _save_attn_index(idx_prov.rename(columns={
            prov_col: 'province', '_total': 'total_articles',
            '_ft': 'fintech_articles'}), '40_attn_index_province_year')

        panel = _merge_geo_index_to_panel(
            df_all, panel, idx_prov[[prov_col, 'year', 'ft_attn_prov']],
            prov_col, 'ft_attn_prov')
        n_prov = idx_prov[prov_col].nunique()
        logger.info(f"  Province × Year: {n_prov} 省 × "
                     f"{idx_prov['year'].nunique()} 年 "
                     f"= {len(idx_prov)} 组")
    else:
        logger.warning(f"  列 '{prov_col}' 不存在, 跳过")

    # ═══════════════════════════════════════════════════════
    # (C) City × Year 指数
    # ═══════════════════════════════════════════════════════
    city_col = '城市'
    if city_col in df_unique.columns:
        idx_city = _build_geo_index(df_unique, city_col, 'ft_attn_city',
                                    min_articles=_ATTN_MIN_ARTICLES)
        # 保存中间数据
        _save_attn_index(idx_city.rename(columns={
            city_col: 'city', '_total': 'total_articles',
            '_ft': 'fintech_articles'}), '40_attn_index_city_year')

        panel = _merge_geo_index_to_panel(
            df_all, panel, idx_city[[city_col, 'year', 'ft_attn_city']],
            city_col, 'ft_attn_city')
        n_city = idx_city[city_col].nunique()
        logger.info(f"  City × Year: {n_city} 市 × "
                     f"{idx_city['year'].nunique()} 年 "
                     f"= {len(idx_city)} 组")
    else:
        logger.warning(f"  列 '{city_col}' 不存在, 跳过")

    # ── 释放内存 ──
    del df_all, df_unique

    # ── 校验 ──
    _validate_attention_index(panel)
    return panel


def _build_geo_index(df_unique, geo_col, val_col, min_articles=5):
    """从唯一文章计算 地理×年度 注意力指数。

    Args:
        df_unique:    按 docid 去重后的唯一文章 DataFrame。
        geo_col:      地理列名 ('国家地区/省份' 或 '城市')。
        val_col:      输出值列名 ('ft_attn_prov' 或 'ft_attn_city')。
        min_articles: 最低文章数阈值。低于此值的 geo×year 不参与
                      指数计算 (避免 1 篇文章产生 0/1 噪声指数)。

    Returns:
        pd.DataFrame: 含 [geo_col, 'year', '_total', '_ft', val_col] 的指数表。
    """
    df_geo = df_unique.dropna(subset=[geo_col])
    total = df_geo.groupby([geo_col, 'year']).size().reset_index(name='_total')
    ft = (df_geo[df_geo['is_fintech_news'] == True]
          .groupby([geo_col, 'year']).size().reset_index(name='_ft'))
    idx = total.merge(ft, on=[geo_col, 'year'], how='left')
    idx['_ft'] = idx['_ft'].fillna(0)

    # 过滤小样本 (避免噪声)
    before = len(idx)
    idx = idx[idx['_total'] >= min_articles]
    dropped = before - len(idx)
    if dropped > 0:
        logger.info(f"    过滤 {dropped} 个 {geo_col}×Year 组 "
                     f"(文章数 < {min_articles})")

    idx[val_col] = idx['_ft'] / idx['_total']
    return idx  # 返回完整列 (含 _total, _ft), 供保存中间数据使用


def _save_attn_index(df, basename):
    """保存注意力指数中间数据 (Parquet + CSV)。"""
    parquet_path = os.path.join(OUTPUT_DIR, f'{basename}.parquet')
    csv_path = os.path.join(OUTPUT_DIR, f'{basename}.csv')
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"    已保存: {basename} ({len(df)} 行)")


def _merge_geo_index_to_panel(df_all, panel, idx_geo,
                               geo_col, target_col):
    """将地理注意力指数通过曝露度加权合并到 Bank-Year 面板。

    合并策略 (Exposure-weighted average):
      1. df_all 中每行 = (article, target_bank), 含媒体来源地
      2. 为每行匹配其来源地的 attention index
      3. 按 (target_bank, year) 取均值
         → "报道该银行的全部媒体所在地区的平均金融科技关注度"

    ⚠️ 权重基于 df_all (含 fintech + non-fintech 全量银行新闻),
       确保地理曝露反映银行的真实媒体环境, 而非仅金融科技新闻的分布。

    Returns:
        panel: 附加 target_col 列的面板。
    """
    # 1. 选取需要的列并清洗
    work = df_all[['target_bank', 'year', geo_col]].copy()
    work = work.dropna(subset=[geo_col])

    # 2. 匹配地理指数
    work = work.merge(idx_geo, on=[geo_col, 'year'], how='left')
    # left join miss → 该 geo×year 被 min_articles 过滤掉, 值为 NaN, 不参与均值

    # 3. Bank-Year 均值
    bank_yr = (work.groupby(['target_bank', 'year'])[target_col]
               .mean().reset_index())

    # 4. 安全合并到 panel (避免 .values 位置赋值的脆弱性)
    if target_col in panel.columns:
        panel = panel.drop(columns=[target_col])
    panel = panel.merge(bank_yr, on=['target_bank', 'year'], how='left')

    matched = panel[target_col].notna().sum()
    logger.info(f"    {target_col}: 匹配 {matched}/{len(panel)} "
                f"({matched/len(panel)*100:.1f}%)")
    return panel


def _validate_attention_index(panel):
    """校验注意力指数变量。"""
    for col in ['ft_attn_yr', 'ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        valid = panel[col].dropna()
        if len(valid) == 0:
            logger.warning(f"  ⚠️ {col}: 全为 NaN")
            continue
        if not valid.between(0, 1).all():
            logger.error(f"  ✗ {col}: 含超出 [0,1] 的值!")
        else:
            logger.info(f"  ✓ {col}: mean={valid.mean():.4f}, "
                         f"std={valid.std():.4f}, "
                         f"[{valid.min():.4f}, {valid.max():.4f}]")

    # year-level 常量校验
    if 'ft_attn_yr' in panel.columns:
        _std = (panel.dropna(subset=['ft_attn_yr'])
                .groupby('year')['ft_attn_yr'].std())
        max_std = _std.max()  # NaN if all groups have n=1
        if pd.isna(max_std) or max_std <= 1e-10:
            logger.info("  ✓ ft_attn_yr 为 year-level 常量")
        else:
            logger.error("  ✗ ft_attn_yr 在同年内取值不一致!")

    # 地理指数截面变异校验
    for col in ['ft_attn_prov', 'ft_attn_city']:
        if col not in panel.columns:
            continue
        within_std = (panel.dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()  # NaN if all groups have n=1
        if pd.isna(mean_std):
            logger.info(f"  ✓ {col}: 各年均仅 1 个银行, 无法计算年内 std")
        elif mean_std < 1e-6:
            logger.warning(f"  ⚠️ {col}: 年内几乎无变异 (退化为 year-level)")
        else:
            logger.info(f"  ✓ {col}: 年内 std 均值={mean_std:.6f}")


# ============================================================================
# 6c. 媒体信息中介异质性 - 四维度 (Bushee et al. 2010, JAR)
# ============================================================================

def compute_media_heterogeneity(df, panel):
    """计算媒体信息中介异质性变量 - 四维度分析。

    四维度:
      1. 财经 vs 其他: 财经类报章 (15家) 与非财经类
      2. 综合 vs 其他: 综合性报章 (27家) 与非综合性
      3. 财经 vs 综合 vs 其他: 三方分拆
      4. 中央级 vs 地方级: CNKI 171家中央级 vs 其余
         (Qin, Strömberg & Wu 2018, AER)

    数据源: config/media_classification.json
    """
    if '媒体(中文)' not in df.columns:
        logger.warning("  媒体列不存在, 跳过")
        return panel

    logger.info("=" * 60)
    logger.info("步骤 6c: 媒体信息中介异质性 - 四维度")
    logger.info("=" * 60)

    # ── 加载媒体分类名单 ──
    config_dir = os.path.dirname(os.path.abspath(
        CONFIG['paths'].get('media_weights_file', '')))
    cls_path = os.path.join(config_dir, 'media_classification.json')
    if not os.path.exists(cls_path):
        logger.warning(f"  {cls_path} 不存在, 跳过")
        return panel

    with open(cls_path, 'r', encoding='utf-8') as f:
        media_cls = json.load(f)
    FIN = set(media_cls.get('financial_media', []))
    COMP = set(media_cls.get('comprehensive_media', []))
    CENTRAL = set(media_cls.get('central_media', []))
    logger.info(f"  财经类: {len(FIN)} 家, 综合性: {len(COMP)} 家, "
                f"中央级: {len(CENTRAL)} 家")

    # 防御性检查: 财经/综合不应重叠 (中央级与其正交, 允许重叠)
    overlap_fc = FIN & COMP
    if overlap_fc:
        logger.warning(f"  ⚠️ FIN ∩ COMP 重叠: {overlap_fc} (将归类为 fin)")
    # 信息性日志: 中央级与财经/综合的交叉
    fc_in_central = (FIN | COMP) & CENTRAL
    if fc_in_central:
        logger.info(f"  ℹ️ 财经/综合 ∩ 中央级: {len(fc_in_central)} 家 "
                    f"(正交分类, 合理)")

    # ── 维度①②③: 财经/综合/其他 三方分类 ──
    def _classify_content(name):
        if name in FIN:
            return 'fin'
        elif name in COMP:
            return 'comp'
        else:
            return 'other'
    df['_media_type'] = df['媒体(中文)'].apply(_classify_content)

    # 诊断
    vc = df['_media_type'].value_counts()
    for mt in ['fin', 'comp', 'other']:
        n = vc.get(mt, 0)
        logger.info(f"    内容分类 - {mt}: {n:,} ({n/len(df)*100:.1f}%)")

    # (1) 占比 - 维度①②
    for mt, col in [('fin', 'fin_media_frac'), ('comp', 'comp_media_frac')]:
        df[f'_is_{mt}'] = (df['_media_type'] == mt).astype(int)
        frac = (df.groupby(['target_bank', 'year'])[f'_is_{mt}']
                .mean().reset_index(name=col))
        panel = panel.merge(frac, on=['target_bank', 'year'], how='left')

    # (2) 三类型情感均值 + 三维度缺口 - 维度①②③
    for track in ['_full', '_ctx']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for mt, sfx in [('fin', 'fin'), ('comp', 'comp'), ('other', 'other')]:
            tone = (df[df['_media_type'] == mt]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        # 缺口
        panel[f'tone_gap_fin_other{track}'] = (
            panel.get(f'tone_fin_media{track}', np.nan)
            - panel.get(f'tone_other_media{track}', np.nan))
        panel[f'tone_gap_comp_other{track}'] = (
            panel.get(f'tone_comp_media{track}', np.nan)
            - panel.get(f'tone_other_media{track}', np.nan))
        panel[f'tone_gap_fin_comp{track}'] = (
            panel.get(f'tone_fin_media{track}', np.nan)
            - panel.get(f'tone_comp_media{track}', np.nan))

    # ── 维度④: 中央级 vs 地方级 (行政层级分类, 与①②③正交) ──
    df['_is_central'] = df['媒体(中文)'].isin(CENTRAL).astype(int)
    n_central = df['_is_central'].sum()
    logger.info(f"    行政分类 - 中央级: {n_central:,} "
                f"({n_central/len(df)*100:.1f}%)")

    # (3) 中央级占比
    frac_c = (df.groupby(['target_bank', 'year'])['_is_central']
              .mean().reset_index(name='central_media_frac'))
    panel = panel.merge(frac_c, on=['target_bank', 'year'], how='left')

    # (4) 中央/地方情感均值 + 缺口
    for track in ['_full', '_ctx']:
        src = f'llm_vote_score{track}'
        if src not in df.columns:
            continue
        for is_c, sfx in [(1, 'central'), (0, 'local')]:
            tone = (df[df['_is_central'] == is_c]
                    .groupby(['target_bank', 'year'])[src]
                    .mean().reset_index(name=f'tone_{sfx}_media{track}'))
            panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
        panel[f'tone_gap_central_local{track}'] = (
            panel.get(f'tone_central_media{track}', np.nan)
            - panel.get(f'tone_local_media{track}', np.nan))

    # ── (5) 媒体来源 HHI ──
    def _hhi(group):
        s = group.value_counts(normalize=True)
        return (s ** 2).sum()
    hhi = (df.groupby(['target_bank', 'year'])['媒体(中文)']
           .apply(_hhi).reset_index(name='media_hhi'))
    panel = panel.merge(hhi, on=['target_bank', 'year'], how='left')

    # ── 清理 ──
    temp = [c for c in df.columns
            if c.startswith('_is_') or c == '_media_type']
    df.drop(columns=temp, inplace=True)
    logger.info("  已生成: fin/comp/central_media_frac, "
                "四维度 tone_gap, media_hhi")

    # ── 校验 (方案断言 5-7) ──
    # (5) 占比值域 [0, 1]
    for col in ['fin_media_frac', 'comp_media_frac', 'central_media_frac',
                'media_hhi']:
        if col in panel.columns:
            valid = panel[col].dropna()
            if len(valid) > 0 and not valid.between(0, 1).all():
                logger.error(f"  ✗ {col}: 含超出 [0,1] 的值!")
            elif len(valid) > 0:
                logger.info(f"  ✓ {col}: [{valid.min():.4f}, {valid.max():.4f}]")

    # (6) 内容分类互斥: fin + comp <= 1
    if 'fin_media_frac' in panel.columns and 'comp_media_frac' in panel.columns:
        _sum = panel['fin_media_frac'].fillna(0) + panel['comp_media_frac'].fillna(0)
        if (_sum > 1.0001).any():
            logger.error("  ✗ fin + comp 占比之和超过 1!")
        else:
            logger.info("  ✓ fin + comp 互斥约束成立")

    # (7) 中央级与内容分类正交 (无需 <= 1 校验, 仅记录交叉统计)
    logger.info("  ✓ 中央级与内容分类为正交分类 (无互斥约束)")

    return panel


# ============================================================================
# 7. 面板级综合指标计算
# ============================================================================

def compute_composite_indicators(panel: pd.DataFrame) -> pd.DataFrame:
    """在面板 DataFrame 上计算综合指标。"""
    logger.info("=" * 60)
    logger.info("步骤 7: 面板级综合指标计算")
    logger.info("=" * 60)

    def _safe_mean(cols):
        """取存在列的行均值。"""
        existing = [c for c in cols if c in panel.columns]
        if existing:
            return panel[existing].mean(axis=1)
        return pd.Series(np.nan, index=panel.index)

    # --- LLM 逐模型综合 ---
    for track in ['_full', '_ctx']:
        panel[f'llm_models_avg_tone{track}'] = _safe_mean([f'{s}_tone{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_tone_sum{track}'] = _safe_mean([f'{s}_tone_sum{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_cont{track}'] = _safe_mean([f'{s}_cont_mean{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_cont_sum{track}'] = _safe_mean([f'{s}_cont_sum{track}' for s in LLM_MODELS])
        panel[f'llm_models_avg_tone_std{track}'] = _safe_mean([f'{s}_tone_std{track}' for s in LLM_MODELS])

        # --- 词典法综合 ---
        panel[f'dict_avg_tone{track}'] = _safe_mean([f'{d}_tone{track}' for d in DICT_NAMES])
        panel[f'dict_avg_tone_sum{track}'] = _safe_mean([f'{d}_tone_sum{track}' for d in DICT_NAMES])
        panel[f'dict_avg_tone_std{track}'] = _safe_mean([f'{d}_tone_std{track}' for d in DICT_NAMES])

        # --- 词典法 IDF 综合 (Gentzkow, Kelly & Taddy 2019, JEL) ---
        panel[f'dict_avg_idf_tone{track}'] = _safe_mean([f'{d}_idf_tone{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_sum{track}'] = _safe_mean([f'{d}_idf_tone_sum{track}' for d in DICT_NAMES])

        # --- BERT 综合 ---
        panel[f'bert_avg_pos{track}'] = _safe_mean([f'{b}_pos{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg{track}'] = _safe_mean([f'{b}_neg{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neu{track}'] = _safe_mean([f'{b}_neu{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        panel[f'bert_avg_pos_sum{track}'] = _safe_mean([f'{b}_pos_sum{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_sum{track}'] = _safe_mean([f'{b}_neg_sum{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neu_sum{track}'] = _safe_mean([f'{b}_neu_sum{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])
        panel[f'bert_avg_pos_std{track}'] = _safe_mean([f'{b}_pos_std{track}' for b in BERT_MODELS])

        # --- VW 综合指标 ---
        panel[f'llm_models_avg_tone_vw{track}'] = _safe_mean([f'{s}_tone_vw{track}' for s in LLM_MODELS])
        panel[f'dict_avg_tone_vw{track}'] = _safe_mean([f'{d}_tone_vw{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_vw{track}'] = _safe_mean([f'{d}_idf_tone_vw{track}' for d in DICT_NAMES])
        panel[f'bert_avg_pos_vw{track}'] = _safe_mean([f'{b}_pos_vw{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_vw{track}'] = _safe_mean([f'{b}_neg_vw{track}' for b in BERT_MODELS])

        # --- MW 综合指标 (Holzman et al. 2023, TAR) ---
        panel[f'llm_models_avg_tone_mw{track}'] = _safe_mean([f'{s}_tone_mw{track}' for s in LLM_MODELS])
        panel[f'dict_avg_tone_mw{track}'] = _safe_mean([f'{d}_tone_mw{track}' for d in DICT_NAMES])
        panel[f'dict_avg_idf_tone_mw{track}'] = _safe_mean([f'{d}_idf_tone_mw{track}' for d in DICT_NAMES])
        panel[f'bert_avg_pos_mw{track}'] = _safe_mean([f'{b}_pos_mw{track}' for b in BERT_MODELS])
        panel[f'bert_avg_neg_mw{track}'] = _safe_mean([f'{b}_neg_mw{track}' for b in BERT_MODELS])

    logger.info(f"  生成双轨综合指标完成")

    # --- 文章平均长度 (He et al. 2024, IRFA, Panel A.5: MLENGTH) ---
    # MLENGTH = ln(文章词数), 此处取 Bank-Year 均值后 ln 变换
    if 'avg_doc_length' in panel.columns:
        panel['avg_article_length'] = np.log1p(panel['avg_doc_length'])
        logger.info(f"  avg_article_length (MLENGTH proxy) 已生成")

    # --- 分类维度综合指标 ---
    for suffix in ['_tech', '_app']:
        # 仅当分类计数列存在时生成
        if f'n_articles{suffix}' not in panel.columns:
            continue

        for track in ['_full', '_ctx']:
            # LLM 逐模型综合
            panel[f'llm_models_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{s}_tone{suffix}{track}' for s in LLM_MODELS])
            panel[f'llm_models_avg_cont{suffix}{track}'] = _safe_mean(
                [f'{s}_cont_mean{suffix}{track}' for s in LLM_MODELS])

            # 词典法综合
            panel[f'dict_avg_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_tone{suffix}{track}' for d in DICT_NAMES])

            # 词典法 IDF 综合
            panel[f'dict_avg_idf_tone{suffix}{track}'] = _safe_mean(
                [f'{d}_idf_tone{suffix}{track}' for d in DICT_NAMES])

            # BERT 综合
            panel[f'bert_avg_pos{suffix}{track}'] = _safe_mean(
                [f'{b}_pos{suffix}{track}' for b in BERT_MODELS])
            panel[f'bert_avg_neg{suffix}{track}'] = _safe_mean(
                [f'{b}_neg{suffix}{track}' for b in BERT_MODELS])
            panel[f'bert_avg_neu{suffix}{track}'] = _safe_mean(
                [f'{b}_neu{suffix}{track}' for b in BERT_MODELS if b in THREE_CLASS_MODELS])

        logger.info(f"  分类 {suffix} 综合指标生成完成")

    # ─── Fintech Exposure 复合指标 (Dim et al. 2024, Eq. 3 概念迁移) ───
    # 概念类比:
    #   论文: NarrativeExposure_n = Σ|β_n,l^narr| × σ(θ_l) / Σσ(θ_l)
    #     |β| = 资产对特定叙事注意力冲击的敏感度
    #     σ(θ) = 叙事注意力的时间序列波动率
    #   本项目: FintechExposure_i,t = ln_coverage_i,t × tone_std_i,t
    #     ln_coverage 类比 |β| → 银行在 fintech 叙事中的信息暴露强度
    #     tone_std 类比 σ(θ) → fintech 报道情感的离散程度
    #   乘积含义: 高覆盖 + 高波动 = 高叙事暴露度
    logger.info("  ─── Fintech Exposure 复合指标 ───")
    has_news = panel['n_articles'] > 0
    for track in ['_full', '_ctx']:
        std_col = f'llm_vote_tone_std{track}'
        if std_col in panel.columns and 'ln_news_coverage' in panel.columns:
            # 零新闻行 → NaN (与面板情感变量 NaN 语义一致)
            coverage = panel['ln_news_coverage'].where(has_news, np.nan)
            panel[f'fintech_exposure{track}'] = coverage * panel[std_col]
            valid = panel[f'fintech_exposure{track}'].dropna()
            logger.info(f"  fintech_exposure{track}: "
                        f"mean={valid.mean():.4f}, "
                        f"std={valid.std():.4f}, "
                        f"非空={len(valid):,}")
        else:
            panel[f'fintech_exposure{track}'] = np.nan
            logger.warning(f"  fintech_exposure{track}: "
                          f"缺少 {std_col} 或 ln_news_coverage, 填 NaN")

    return panel


# ============================================================================
# 7b. 年度截面标准化 (Fama & MacBeth 1973)
# ============================================================================

# 核心回归变量白名单 (仅这些列生成 _z 后缀)
_STANDARDIZE_COLS = [
    # LLM 投票 (主指标)
    'llm_vote_tone_{t}', 'llm_vote_cont_{t}',
    # LLM 逐模型综合
    'llm_models_avg_tone_{t}', 'llm_models_avg_cont_{t}',
    # 词典法综合
    'dict_avg_tone_{t}', 'dict_avg_idf_tone_{t}',
    # BERT 综合
    'bert_avg_pos_{t}', 'bert_avg_neg_{t}',
    # VW 加权
    'llm_vote_tone_vw_{t}', 'dict_avg_tone_vw_{t}',
    # MW 加权 (Holzman 2023)
    'llm_vote_tone_mw_{t}', 'dict_avg_tone_mw_{t}',
    # MSENT (He et al. 2024)
    'avg_msent_{t}',
    # Fintech Exposure (Dim et al. 2024 概念迁移)
    'fintech_exposure_{t}',
]
# 无双轨的标量变量
_STANDARDIZE_SCALAR = [
    'ln_news_coverage', 'media_breadth',
    'avg_article_length',
]


def _expand_track_templates(templates: list) -> list:
    """将含 {t} 占位符的模板展开为 _full 和 _ctx 两个变量名。"""
    result = []
    for tmpl in templates:
        if '{t}' in tmpl:
            result.append(tmpl.replace('{t}', 'full'))
            result.append(tmpl.replace('{t}', 'ctx'))
        else:
            result.append(tmpl)
    return result


def standardize_panel_variables(panel: pd.DataFrame) -> pd.DataFrame:
    """年度截面标准化: 核心回归变量在每个年度截面内归至单位方差。

    学术依据:
      Fama, E.F. & MacBeth, J.D. (1973, JPE, 71, 607-636):
        两阶段回归要求截面变量可比, 标准化确保系数
        可直接解读为 "1σ 变化对应 β 个单位的因变量变动"。

    操作:
      1. 仅处理有新闻覆盖的 Bank-Year (n_articles > 0)
      2. 对白名单内的核心回归变量执行年度截面 z-score
      3. 生成 _z 后缀列, 保留原始列不变
      4. 零新闻行保持 NaN

    输出列命名: 原列名 + '_z'
    """
    logger.info("=" * 60)
    logger.info("步骤 7b: 年度截面标准化 (Fama-MacBeth 1973)")
    logger.info("=" * 60)

    # ── 展开白名单 ──
    target_cols = (_expand_track_templates(_STANDARDIZE_COLS)
                   + _STANDARDIZE_SCALAR)
    valid_cols = [c for c in target_cols
                  if c in panel.columns
                  and panel[c].notna().sum() >= 10]
    skipped = [c for c in target_cols
               if c in panel.columns
               and panel[c].notna().sum() < 10]
    missing = [c for c in target_cols if c not in panel.columns]

    logger.info(f"  白名单总数: {len(target_cols)}, "
                f"有效: {len(valid_cols)}, "
                f"观测不足跳过: {len(skipped)}, "
                f"列不存在: {len(missing)}")
    if skipped:
        logger.info(f"    跳过(观测<10): {skipped}")

    # ── 执行年度截面 z-score ──
    has_news = panel['n_articles'] > 0
    z_count = 0

    for col in valid_cols:
        z_col = f'{col}_z'
        panel[z_col] = np.nan

        for year, grp in panel[has_news].groupby('year'):
            vals = grp[col].dropna()
            if len(vals) < 3:
                continue
            mu = vals.mean()
            sigma = vals.std()
            if sigma < 1e-10:
                continue
            idx = grp.index
            panel.loc[idx, z_col] = (panel.loc[idx, col] - mu) / sigma

        z_count += 1

    logger.info(f"  已生成 {z_count} 个 _z 标准化列")

    # ── 校验: 标准化后年内 std ≈ 1 ──
    sample_z_cols = [c for c in panel.columns if c.endswith('_z')][:5]
    for col in sample_z_cols:
        within_std = (panel[has_news].dropna(subset=[col])
                      .groupby('year')[col].std())
        mean_std = within_std.mean()
        if pd.notna(mean_std):
            ok = '✓' if abs(mean_std - 1.0) < 0.1 else '⚠️'
            logger.info(f"  校验 {col}: 年内 std 均值 = "
                        f"{mean_std:.4f} {ok}")

    return panel


# ============================================================================
# 7c. 银行注册地地理信息合并
# ============================================================================
# 学术背景:
#   在面板回归中, 标准误的聚类层级选择直接影响推断的可靠性。
#   当误差项存在组内相关时 (如同省银行受共同的地方政策、媒体生态影响),
#   在银行层级聚类会低估标准误, 导致 t 统计量虚高。
#
#   Luo & Li (2025, FRL, Table A.2 Col. 3) 使用省级聚类标准误
#   作为稳健性检验, 其核心逻辑是: 地理相近的银行面临相似的
#   媒体报道环境 (同一批地方媒体、相似的编辑倾向), 导致
#   情感得分在省内具有正相关性, 需要通过更高层级的聚类来校正。
#
#   本步骤从 bank_addresses.json 提取每家银行总行注册地的省份和城市,
#   供 Stata 回归中灵活选择聚类层级:
#     - vce(cluster bank_city)     → 329 个聚类, 超过 50 个门槛, 推断可靠
#     - vce(cluster bank_province) → 31 个聚类, 低于 50 个门槛, 需补充 wild bootstrap
#
# 参考文献:
#   [1] Luo, Q. & Li, H. (2025). "Media sentiment and corporate R&D manipulation."
#       Finance Research Letters, 81, 107505.
#   [2] Gurun, U.G. & Butler, A.W. (2012). "Don't Believe the Hype."
#       The Journal of Finance, 67(2), 561-598.
#   [3] Cameron, A.C. & Miller, D.L. (2015). "A Practitioner's Guide to
#       Cluster-Robust Inference." Journal of Human Resources, 50(2), 317-372.
# ============================================================================

def merge_bank_geography(panel: pd.DataFrame) -> pd.DataFrame:
    """步骤 7c: 合并银行注册地地理信息 (省份 + 城市)。

    本函数将 bank_addresses.json 中的银行总行注册地信息 (省份、城市)
    通过 target_bank 列名映射到 Bank-Year 面板中。合并后的地理变量
    有两个核心用途:

    用途 1 — 地理层级递进聚类标准误 (Stata):
      标准面板回归使用银行级聚类 vce(cluster target_bank), 但当扰动项
      在地理维度存在空间自相关时 (如同省银行共同受地方媒体生态影响),
      银行级聚类会低估标准误。通过逐级提升聚类层级:
        银行级 (N≈1768) → 城市级 (329) → 省级 (31)
      可检验系数显著性对聚类层级的稳健性。

      ⚠️ Cameron & Miller (2015, JHR) 指出: 聚类数 < 50 时,
      渐近正态近似不准确, 标准聚类标准误可能偏小。
      31 个省级聚类低于此门槛, 建议在 Stata 中补充
      wild cluster bootstrap (boottest 命令) 进行确认。

    用途 2 — Leave-one-out 工具变量的前置依赖:
      步骤 7d 需要知道每家银行所在的省份/城市, 才能计算
      "同省/同城市其他银行的平均情感" (leave-one-out IV)。
      本函数是 7d 的必要前置步骤。

    数据源:
      config/bank_addresses.json
      结构: {bank_name: {province, city, district, address}}
      覆盖: 1768 条记录 (含中国人民银行), 31 个省级行政区, 329 个城市
      匹配: bank_names.json 中 1767 家银行全部包含在 bank_addresses 中
            (addresses 多出的 1 条为 "中国人民银行", 不在面板 target_bank 中)

    新增列:
      bank_province — 银行总行注册所在的省级行政区
                      (直辖市单独列出, 如 "北京"、"上海")
                      Stata 用途: vce(cluster bank_province),
                                  absorb(bank_province) [替换银行FE时]
      bank_city     — 银行总行注册所在的城市
                      Stata 用途: vce(cluster bank_city)

    填充策略:
      未匹配银行 → 空字符串 '' (非 NaN)
      原因: Stata 的 cluster() 对 NaN 会报错, 空字符串可被安全忽略

    Args:
        panel: Bank-Year 面板 DataFrame, 须含 'target_bank' 列。

    Returns:
        panel: 附加 'bank_province' 和 'bank_city' 列的 DataFrame。
    """
    logger.info("=" * 60)
    logger.info("步骤 7c: 合并银行注册地地理信息 (Luo & Li 2025)")
    logger.info("=" * 60)
    logger.info("  学术依据: Luo & Li (2025, FRL, Table A.2)")
    logger.info("  聚类推断: Cameron & Miller (2015, JHR, 50(2), 317-372)")

    # ── 加载 bank_addresses.json ──
    # 路径优先从 config.yaml 的 paths.bank_addresses_file 读取,
    # 未配置时回退到项目默认路径 config/bank_addresses.json
    addr_path = CONFIG['paths'].get(
        'bank_addresses_file',
        os.path.join(os.path.dirname(__file__), 'config', 'bank_addresses.json')
    )
    if not os.path.exists(addr_path):
        logger.warning(f"  bank_addresses_file 不存在: {addr_path}, 跳过")
        # 即使文件不存在也生成空列, 确保后续步骤不会因列缺失报错
        panel['bank_province'] = ''
        panel['bank_city'] = ''
        return panel

    with open(addr_path, 'r', encoding='utf-8') as f:
        addr_data = json.load(f)
    logger.info(f"  已加载 {len(addr_data)} 条银行地址")

    # ── 构建 bank_name → province/city 映射 ──
    # bank_addresses.json 的 key 是银行标准全称 (与 bank_names.json 的
    # bank_name 字段一致), 与面板中的 target_bank 列直接对应
    prov_map = {k: v.get('province', '') for k, v in addr_data.items()}
    city_map = {k: v.get('city', '') for k, v in addr_data.items()}

    # ── 通过 target_bank 列映射到面板 ──
    # 使用 .map() 而非 merge, 因为是简单的 key → value 映射
    # .fillna('') 将未匹配的银行填为空字符串 (非 NaN)
    panel['bank_province'] = panel['target_bank'].map(prov_map).fillna('')
    panel['bank_city'] = panel['target_bank'].map(city_map).fillna('')

    # ── 匹配率诊断 ──
    matched = (panel['bank_province'] != '').sum()
    total = len(panel)
    logger.info(f"  匹配率: {matched}/{total} "
                f"= {matched / max(total, 1) * 100:.1f}%")

    # 输出未匹配银行名单 (帮助调试 bank_names 与 bank_addresses 的不一致)
    unmatched_banks = panel.loc[
        panel['bank_province'] == '', 'target_bank'
    ].unique()
    if len(unmatched_banks) > 0:
        logger.warning(f"  未匹配银行 ({len(unmatched_banks)}): "
                       f"{list(unmatched_banks)[:10]}")
    else:
        logger.info("  ✓ 全部银行匹配成功")

    # ── 聚类数统计 ──
    # Cameron & Miller (2015, JHR) 实证研究表明:
    #   聚类数 ≥ 50: 标准渐近推断 (Wald test, t-test) 可靠
    #   聚类数 < 50: 标准误可能偏小, 建议使用 wild cluster bootstrap
    n_prov = panel[panel['bank_province'] != '']['bank_province'].nunique()
    n_city = panel[panel['bank_city'] != '']['bank_city'].nunique()
    logger.info(f"  省份聚类数: {n_prov} "
                f"{'⚠️ < 50, 建议补充 wild cluster bootstrap' if n_prov < 50 else '✓ ≥ 50'}")
    logger.info(f"  城市聚类数: {n_city} "
                f"{'⚠️ < 50' if n_city < 50 else '✓ ≥ 50'}")

    # ── 分布摘要 (供审查地理覆盖合理性) ──
    prov_dist = panel[panel['bank_province'] != '']['bank_province'].value_counts()
    city_dist = panel[panel['bank_city'] != '']['bank_city'].value_counts()
    logger.info(f"  省份 Top-5: {dict(prov_dist.head())}")
    logger.info(f"  城市 Top-5: {dict(city_dist.head())}")

    return panel


# ============================================================================
# 7d. Leave-one-out 地理平均情感工具变量
# ============================================================================
# 学术背景:
#   在媒体情感 → 企业行为的回归中, 情感变量可能存在内生性:
#     (1) 反向因果: 企业行为 (如 R&D 操纵) 引发媒体报道, 而非相反
#     (2) 遗漏变量: 不可观测的企业特征同时影响媒体报道和企业行为
#
#   工具变量法 (IV) 是处理内生性的标准方法。有效 IV 须满足:
#     相关性 (relevance): IV 与内生变量显著相关
#     排他性 (exclusion): IV 仅通过内生变量影响因变量
#
#   Luo & Li (2025, FRL, Table 3) 使用 Province_news_sentiment 作为 IV:
#     定义: 同省份内排除目标企业后, 其余企业的年度平均新闻情感
#     相关性: 同省银行面临相同的地方媒体生态 (编辑倾向、记者网络),
#             导致情感得分在省内正相关
#     排他性: 其他银行的平均媒体情感反映的是省级媒体环境的整体偏向,
#             不会直接影响目标银行的 R&D 操纵决策
#
#   本步骤同时构建省级和城市级两个层次的 leave-one-out IV:
#     - 省级: 31 个省, 每省包含较多银行, IV 变异来源更宏观
#     - 城市级: 329 个城市, IV 变异更精细, 第一阶段 F 统计量通常更高
#
#   两个层级的 IV 可同时用于过度识别检验 (Hansen J test),
#   检验排他性约束是否同时成立。
#
# 与 ft_attn_prov/city 的区别:
#   ft_attn_prov/city (已在面板, Bhojraj et al. 2025):
#     = 报道该银行的媒体来源地的金融科技文章占比
#     → 捕获的是 "媒体关注度" 维度的外生变异
#
#   prov/city_leave1out_tone (本步骤构建):
#     = 同省/城市其他银行的平均情感得分 (排除自身)
#     → 捕获的是 "情感溢出" 维度的外生变异 (直接对标论文)
#
#   两者从不同角度提供了外生变异, 可同时作为 IV 进行 overid test。
#
# 参考文献:
#   [1] Luo, Q. & Li, H. (2025). "Media sentiment and corporate R&D
#       manipulation." Finance Research Letters, 81, 107505. Table 3.
# ============================================================================

# 地理列 → 输出变量名前缀的缩写映射
# 避免 geo_col.replace("bank_","") 生成 "province_leave1out_tone_full" (28字符)
# 而 Stata 模板和 LABELS 使用 "prov_leave1out_tone_full" (25字符) 的不一致
_GEO_SHORT = {'bank_province': 'prov', 'bank_city': 'city'}

def compute_leave_one_out_sentiment(panel: pd.DataFrame) -> pd.DataFrame:
    """步骤 7d: 构建 Leave-one-out 地理平均情感工具变量。

    对于面板中每个 Bank-Year 观测 (i, t), 计算同省/同城市内
    排除银行 i 后其余银行的年度平均情感得分:

      leave1out_{i,t} = (Σ_{j≠i, j∈G} tone_{j,t}) / (N_{G,t} - 1)

    其中 G 是银行 i 所在的省份或城市, N_{G,t} 是该年度 G 内
    有有效情感得分 (非 NaN) 的银行数量。

    计算使用向量化 leave-one-out 公式 (O(N) 复杂度):
      group_sum = Σ tone_j (组内所有银行含自身)
      group_cnt = N (组内有效银行数)
      leave1out_i = (group_sum - tone_i) / (group_cnt - 1)

    边界情况处理:
      - 某省/城市某年仅 1 家银行有情感数据 → leave-one-out 为 NaN
        (无法从自身推断同地区媒体生态, 这是方法论上正确的处理)
      - 银行无新闻报道 (tone = NaN) → 不参与分组计算且自身结果为 NaN
      - 银行无地理标识 (bank_province = '') → 不参与计算

    依赖:
      须在 merge_bank_geography() (步骤 7c) 之后调用,
      因为需要 bank_province 和 bank_city 列。
      须在 balance_panel() (步骤 6) 之后调用,
      因为 leave-one-out 公式假设每家银行在 (geo, year) 内
      仅出现一次 (balance_panel 保证 target_bank×year 唯一)。

    新增列 (双层 × 双轨道 = 4 个变量):
      prov_leave1out_tone_full — 省级 leave-one-out, Full 轨道
      prov_leave1out_tone_ctx  — 省级 leave-one-out, Ctx 轨道
      city_leave1out_tone_full — 城市级 leave-one-out, Full 轨道
      city_leave1out_tone_ctx  — 城市级 leave-one-out, Ctx 轨道

    变量命名:
      使用 _GEO_SHORT 映射确保缩写一致:
        bank_province → 'prov', bank_city → 'city'
      避免 .replace("bank_","") 生成过长的 "province_" 前缀

    Stata 用途:
      ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) X,
        absorb(target_bank year) cluster(target_bank)

    Args:
        panel: Bank-Year 面板, 须含 bank_province, bank_city,
               llm_vote_tone_full, llm_vote_tone_ctx, year 列。

    Returns:
        panel: 附加 4 个 leave-one-out 列的 DataFrame。
    """
    logger.info("=" * 60)
    logger.info("步骤 7d: Leave-one-out 地理平均情感 (Luo & Li 2025)")
    logger.info("=" * 60)
    logger.info("  对标: Province_news_sentiment (Table 3)")
    logger.info("  公式: leave1out_i = (Σ tone_j - tone_i) / (N - 1), j ≠ i")

    for geo_col, geo_label in [('bank_province', '省级'),
                                ('bank_city', '城市级')]:
        # 检查地理列是否可用 (非空)
        if geo_col not in panel.columns or (panel[geo_col] == '').all():
            logger.warning(f"  {geo_col} 不可用, 跳过 {geo_label}")
            continue

        for track in ['_full', '_ctx']:
            tone_col = f'llm_vote_tone{track}'
            # 使用 _GEO_SHORT 缩写映射, 确保变量名与 Stata 模板一致
            # bank_province → prov_leave1out_tone_full (25字符)
            # bank_city     → city_leave1out_tone_full (24字符)
            out_col = f'{_GEO_SHORT[geo_col]}_leave1out_tone{track}'

            if tone_col not in panel.columns:
                continue

            # ── 筛选有效子集 ──
            # 条件 1: 有地理标识 (排除未匹配银行)
            # 条件 2: 有情感得分 (排除零新闻观测)
            mask = (panel[geo_col] != '') & panel[tone_col].notna()
            subset = panel.loc[mask]

            # ── 向量化 Leave-one-out 计算 ──
            # transform('sum'/'count') 在 groupby 后广播回原索引,
            # 每行获得其所属组 (省/城市 × 年度) 的组内总和和计数
            grp_sum = subset.groupby(
                [geo_col, 'year']
            )[tone_col].transform('sum')
            grp_cnt = subset.groupby(
                [geo_col, 'year']
            )[tone_col].transform('count')

            # ── 赋值 (仅对组内 ≥ 2 家银行的观测) ──
            # grp_cnt == 1: 某省/城市某年仅此一家银行有数据,
            #   leave-one-out 分母为 0, 赋 NaN (方法论正确)
            panel[out_col] = np.nan
            valid_idx = subset.index[grp_cnt > 1]
            panel.loc[valid_idx, out_col] = (
                (grp_sum.loc[valid_idx]
                 - subset.loc[valid_idx, tone_col])
                / (grp_cnt.loc[valid_idx] - 1)
            )

            # ── 诊断日志 ──
            n_valid = panel[out_col].notna().sum()
            n_singleton = mask.sum() - len(valid_idx)
            logger.info(f"  {out_col}: "
                        f"有效={n_valid}, "
                        f"单一银行组={n_singleton}")

    return panel


# ============================================================================
# 8. 诊断统计量
# ============================================================================

def log_diagnostics(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """输出面板诊断统计, 包含分类维度(底层技术/应用场景)的覆盖率和置信度。"""
    logger.info("=" * 60)
    logger.info("步骤 8: 诊断统计量")
    logger.info("=" * 60)

    n_banks = panel['target_bank'].nunique()
    n_years = panel['year'].nunique()
    year_min, year_max = panel['year'].min(), panel['year'].max()

    no_news = (panel['n_articles'] == 0).sum()
    no_news_pct = no_news / len(panel) if len(panel) > 0 else 0

    logger.info(f"  面板维度: {len(panel):,} 行 ({n_banks} 银行 × {n_years} 年)")
    logger.info(f"  时间跨度: {year_min} - {year_max}")
    logger.info(f"  零新闻观测: {no_news:,} ({no_news_pct:.1%})")

    if 'n_articles' in panel.columns:
        logger.info(f"  新闻覆盖量统计:")
        desc = panel['n_articles'].describe()
        logger.info(f"    mean={desc['mean']:.1f}, median={desc['50%']:.0f}, "
                    f"max={desc['max']:.0f}, std={desc['std']:.1f}")

    if 'llm_vote_tone_full' in panel.columns:
        valid_tone = panel['llm_vote_tone_full'].dropna()
        if len(valid_tone) > 0:
            logger.info(f"  LLM 投票情感强度: mean={valid_tone.mean():.4f}, "
                        f"std={valid_tone.std():.4f}")

    # --- 分类维度诊断 ---
    if 'tech_frac' in panel.columns:
        valid_tf = panel['tech_frac'].dropna()
        if len(valid_tf) > 0:
            logger.info(f"  底层技术占比 (tech_frac):")
            logger.info(f"    mean={valid_tf.mean():.3f}, median={valid_tf.median():.3f}, "
                        f"std={valid_tf.std():.3f}")
    for suffix, label in [('_tech', '底层技术'), ('_app', '应用场景')]:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            has_cat = (panel[col] > 0).sum()
            total = (panel['n_articles'] > 0).sum()
            if total > 0:
                logger.info(f"  {label} ({col}): "
                            f"有文章的 Bank-Year = {has_cat}/{total} ({has_cat/total:.1%})")
            else:
                logger.info(f"  {label} ({col}): 无有效新闻观测")
    if 'avg_category_confidence' in panel.columns:
        valid_conf = panel['avg_category_confidence'].dropna()
        if len(valid_conf) > 0:
            logger.info(f"  分类置信度: mean={valid_conf.mean():.3f}, "
                        f"median={valid_conf.median():.3f}")

    # 文章级统计
    logger.info(f"  展开后文章-银行级行数: {len(df_exploded):,}")
    logger.info(f"  多银行文章占比: {df_exploded['is_multi_bank'].mean():.1%}")


# ============================================================================
# 9. 导出
# ============================================================================

def export_panel(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """多格式导出面板数据。"""
    logger.info("=" * 60)
    logger.info("步骤 9: 多格式导出")
    logger.info("=" * 60)

    # 年度面板 Parquet
    panel_filename = FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet')
    panel_path = os.path.join(OUTPUT_DIR, panel_filename)
    save_dataset(panel, panel_path, logger)

    # 年度面板 Stata .dta
    if PANEL_CFG.get('export_stata', True):
        dta_path = os.path.splitext(panel_path)[0] + '.dta'
        try:
            panel_stata = panel.copy()
            # Stata 列名清理：移除中文和特殊字符, 限制 32 字符, 去重
            clean_cols = []
            seen = {}
            for c in panel_stata.columns:
                # 替换中文括号和英文括号
                c_clean = c.replace('(', '_').replace(')', '_')
                c_clean = c_clean.replace('（', '_').replace('）', '_')
                # 移除其他非 ASCII 字符
                c_clean = re.sub(r'[^\x00-\x7F]+', '', c_clean)
                # 确保不为空
                if not c_clean or not c_clean.strip('_'):
                    c_clean = f'col_{len(clean_cols)}'
                # Stata 变量名不超过 32 字符
                c_clean = c_clean[:32]
                # 去重：重复列名追加 _2, _3, ...
                if c_clean in seen:
                    seen[c_clean] += 1
                    c_clean = f'{c_clean[:29]}_{seen[c_clean]}'
                else:
                    seen[c_clean] = 1
                clean_cols.append(c_clean)
            panel_stata.columns = clean_cols
            # 确保数值列没有 nullable dtypes（Stata 不支持）
            for col in panel_stata.select_dtypes(include=['Float64', 'Int64']).columns:
                panel_stata[col] = panel_stata[col].astype(float)
            # 学术级变量标签 (Stata variable labels, ≤80 字符)
            STATA_LABELS = {
                # 注意力指数 (Bhojraj et al. 2025)
                'ft_attn_yr':    'Fintech Attention Index (Year)',
                'ft_attn_prov':  'Fintech Attention (Province, Exp-Wt)',
                'ft_attn_city':  'Fintech Attention (City, Exp-Wt)',
                # 媒体异质性 - 占比
                'fin_media_frac':              'Financial Media Share',
                'comp_media_frac':             'Comprehensive Media Share',
                'central_media_frac':          'Central-Level Media Share',
                # 媒体异质性 - 情感均值 (Full 轨道)
                'tone_fin_media_full':         'Avg Tone: Financial Media (Full)',
                'tone_comp_media_full':        'Avg Tone: Comprehensive Media (Full)',
                'tone_other_media_full':       'Avg Tone: Other Media (Full)',
                'tone_central_media_full':     'Avg Tone: Central Media (Full)',
                'tone_local_media_full':       'Avg Tone: Local Media (Full)',
                # 媒体异质性 - 情感均值 (Ctx 轨道)
                'tone_fin_media_ctx':          'Avg Tone: Financial Media (Ctx)',
                'tone_comp_media_ctx':         'Avg Tone: Comprehensive Media (Ctx)',
                'tone_other_media_ctx':        'Avg Tone: Other Media (Ctx)',
                'tone_central_media_ctx':      'Avg Tone: Central Media (Ctx)',
                'tone_local_media_ctx':        'Avg Tone: Local Media (Ctx)',
                # 媒体异质性 - 情感缺口 (Full 轨道)
                'tone_gap_fin_other_full':     'Tone Gap: Fin - Other (Full)',
                'tone_gap_comp_other_full':    'Tone Gap: Comp - Other (Full)',
                'tone_gap_fin_comp_full':      'Tone Gap: Fin - Comp (Full)',
                'tone_gap_central_local_full': 'Tone Gap: Central - Local (Full)',
                # 媒体异质性 - 情感缺口 (Ctx 轨道)
                'tone_gap_fin_other_ctx':      'Tone Gap: Fin - Other (Ctx)',
                'tone_gap_comp_other_ctx':     'Tone Gap: Comp - Other (Ctx)',
                'tone_gap_fin_comp_ctx':       'Tone Gap: Fin - Comp (Ctx)',
                'tone_gap_central_local_ctx':  'Tone Gap: Central - Local (Ctx)',
                # 集中度
                'media_hhi':                   'Media Source HHI',
                # 媒体权威性加权 (Holzman et al. 2023, TAR)
                'llm_vote_tone_mw_full':          'LLM Vote Tone (Media-Auth Wt, Full)',
                'llm_vote_tone_mw_ctx':           'LLM Vote Tone (Media-Auth Wt, Ctx)',
                'llm_vote_cont_mw_full':          'LLM Vote Cont (Media-Auth Wt, Full)',
                'llm_vote_cont_mw_ctx':           'LLM Vote Cont (Media-Auth Wt, Ctx)',
                'llm_models_avg_tone_mw_full':    'LLM Avg Tone (Media-Auth Wt, Full)',
                'llm_models_avg_tone_mw_ctx':     'LLM Avg Tone (Media-Auth Wt, Ctx)',
                'dict_avg_tone_mw_full':          'Dict Avg Tone (Media-Auth Wt, Full)',
                'dict_avg_tone_mw_ctx':           'Dict Avg Tone (Media-Auth Wt, Ctx)',
                'dict_avg_idf_tone_mw_full':      'Dict IDF Tone (Media-Auth Wt, Full)',
                'dict_avg_idf_tone_mw_ctx':       'Dict IDF Tone (Media-Auth Wt, Ctx)',
                'bert_avg_pos_mw_full':           'BERT Avg Pos (Media-Auth Wt, Full)',
                'bert_avg_pos_mw_ctx':            'BERT Avg Pos (Media-Auth Wt, Ctx)',
                'bert_avg_neg_mw_full':           'BERT Avg Neg (Media-Auth Wt, Full)',
                'bert_avg_neg_mw_ctx':            'BERT Avg Neg (Media-Auth Wt, Ctx)',
                # MSENT 计数型情感 (He et al. 2024, IRFA)
                'avg_msent_full':                 'MSENT (Neg-Pos)/(Neg+Pos) EW Mean (Full)',
                'avg_msent_ctx':                  'MSENT (Neg-Pos)/(Neg+Pos) EW Mean (Ctx)',
                'avg_msent_std_full':              'MSENT Std Dev (Full)',
                'avg_msent_std_ctx':               'MSENT Std Dev (Ctx)',
                # 文章长度 (He et al. 2024, IRFA)
                'avg_article_length':             'Article Length ln(1+avg_words)',
                # Fintech Exposure (Dim et al. 2024 概念迁移)
                'fintech_exposure_full':   'Fintech Exposure (Cov*Std, Full)',
                'fintech_exposure_ctx':    'Fintech Exposure (Cov*Std, Ctx)',
                # 截面标准化 (Fama-MacBeth 1973)
                'llm_vote_tone_full_z':    'LLM Vote Tone Z-scored (Full)',
                'llm_vote_tone_ctx_z':     'LLM Vote Tone Z-scored (Ctx)',
                'llm_vote_cont_full_z':    'LLM Vote Cont Z-scored (Full)',
                'llm_vote_cont_ctx_z':     'LLM Vote Cont Z-scored (Ctx)',
                'dict_avg_tone_full_z':    'Dict Avg Tone Z-scored (Full)',
                'dict_avg_tone_ctx_z':     'Dict Avg Tone Z-scored (Ctx)',
                'ln_news_coverage_z':      'News Coverage ln Z-scored',
                'media_breadth_z':         'Media Breadth Z-scored',
                'fintech_exposure_full_z': 'Fintech Exposure Z (Full)',
                'fintech_exposure_ctx_z':  'Fintech Exposure Z (Ctx)',
                # 银行注册地地理信息 (Luo & Li 2025, FRL, Table A.2)
                # 用途: vce(cluster bank_province), vce(cluster bank_city)
                'bank_province':                   'Bank HQ Province (Registration)',
                'bank_city':                       'Bank HQ City (Registration)',
                # Leave-one-out 地理平均情感 IV (Luo & Li 2025, Table 3)
                # 定义: 同省/同城市其他银行的年度平均情感 (排除自身)
                # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
                'prov_leave1out_tone_full':         'Province Leave-1-Out Tone (Full)',
                'prov_leave1out_tone_ctx':          'Province Leave-1-Out Tone (Ctx)',
                'city_leave1out_tone_full':         'City Leave-1-Out Tone (Full)',
                'city_leave1out_tone_ctx':          'City Leave-1-Out Tone (Ctx)',
                # Bartik IV — 银行类型维度 (主)
                'bank_type':                           'Bank Type (nfra_type)',
                'bartik_type_iv_full':                 'Bartik IV: Bank-Type (Full)',
                'bartik_type_iv_ctx':                  'Bartik IV: Bank-Type (Ctx)',
                'bartik_type_share_soe':               'Bartik Share: SOE Banks',
                'bartik_type_share_joint':             'Bartik Share: Joint-Stock',
                'bartik_type_share_city':              'Bartik Share: City Commercial',
                'bartik_type_share_rural':             'Bartik Share: Rural Commercial',
                'bartik_type_share_private':           'Bartik Share: Private Banks',
                'bartik_type_share_foreign':           'Bartik Share: Foreign Banks',
                # Bartik IV — 规模维度 (稳健性 1)
                'bank_scale':                          'Bank Scale (enterprise_scale)',
                'bartik_scale_iv_full':                'Bartik IV: Bank-Scale (Full)',
                'bartik_scale_iv_ctx':                 'Bartik IV: Bank-Scale (Ctx)',
                'bartik_scale_share_L':                'Bartik Share: Large Banks',
                'bartik_scale_share_M':                'Bartik Share: Medium Banks',
                'bartik_scale_share_S':                'Bartik Share: Small Banks',
                'bartik_scale_share_XS':               'Bartik Share: Micro Banks',
                # Bartik IV — 金融科技类型维度 (稳健性 2)
                'bartik_fintech_iv_full':              'Bartik IV: Fintech-Category (Full)',
                'bartik_fintech_iv_ctx':               'Bartik IV: Fintech-Category (Ctx)',
                'bartik_fintech_share_tech':           'Bartik Share: Technology',
                'bartik_fintech_share_app':            'Bartik Share: Application',
                # Bartik IV — 媒体类型维度 (稳健性 3)
                'bartik_media_iv_full':                'Bartik IV: Media-Type (Full)',
                'bartik_media_iv_ctx':                 'Bartik IV: Media-Type (Ctx)',
                'bartik_media_share_fin':              'Bartik Share: Financial Media',
                'bartik_media_share_comp':             'Bartik Share: Comprehensive Media',
                # Bartik IV — 中央/地方 (稳健性 4)
                'bartik_mcentral_iv_full':             'Bartik IV: Central-Local (Full)',
                'bartik_mcentral_iv_ctx':              'Bartik IV: Central-Local (Ctx)',
                'bartik_mcentral_share_central':       'Bartik Share: Central Media',
                'bartik_mcentral_share_local':         'Bartik Share: Local Media',
                # Bartik IV — 财经/非财经 (稳健性 5)
                'bartik_mfin_iv_full':                 'Bartik IV: Fin-NonFin (Full)',
                'bartik_mfin_iv_ctx':                  'Bartik IV: Fin-NonFin (Ctx)',
                'bartik_mfin_share_fin':               'Bartik Share: Financial',
                'bartik_mfin_share_nonfin':            'Bartik Share: Non-Financial',
                # Bartik IV — 综合类/非综合类 (稳健性 6)
                'bartik_mcomp_iv_full':                'Bartik IV: Comp-NonComp (Full)',
                'bartik_mcomp_iv_ctx':                 'Bartik IV: Comp-NonComp (Ctx)',
                'bartik_mcomp_share_comp':             'Bartik Share: Comprehensive',
                'bartik_mcomp_share_noncomp':          'Bartik Share: Non-Comprehensive',
                # Bartik IV — 媒体省份 (稳健性 7)
                'bartik_mprov_iv_full':                'Bartik IV: Media-Province (Full)',
                'bartik_mprov_iv_ctx':                 'Bartik IV: Media-Province (Ctx)',
                # Bartik IV — 媒体权威性 (稳健性 8)
                'bartik_mauth_iv_full':                'Bartik IV: Media-Authority (Full)',
                'bartik_mauth_iv_ctx':                 'Bartik IV: Media-Authority (Ctx)',
                'bartik_mauth_share_high':             'Bartik Share: High Authority',
                'bartik_mauth_share_mid':              'Bartik Share: Mid Authority',
                'bartik_mauth_share_low':              'Bartik Share: Low Authority',
                # Bartik IV — 文章长度 (稳健性 9)
                'bartik_doclen_iv_full':               'Bartik IV: Doc-Length (Full)',
                'bartik_doclen_iv_ctx':                'Bartik IV: Doc-Length (Ctx)',
                'bartik_doclen_share_long':            'Bartik Share: Long Articles',
                'bartik_doclen_share_short':           'Bartik Share: Short Articles',
                # Bartik IV — 半年度 (稳健性 10)
                'bartik_half_iv_full':                 'Bartik IV: Half-Year (Full)',
                'bartik_half_iv_ctx':                  'Bartik IV: Half-Year (Ctx)',
                'bartik_half_share_H1':                'Bartik Share: First Half',
                'bartik_half_share_H2':                'Bartik Share: Second Half',
                # Bartik IV — 季度 (稳健性 11)
                'bartik_qtr_iv_full':                  'Bartik IV: Quarter (Full)',
                'bartik_qtr_iv_ctx':                   'Bartik IV: Quarter (Ctx)',
                # Bartik IV — 月度 (稳健性 12)
                'bartik_month_iv_full':                'Bartik IV: Month (Full)',
                'bartik_month_iv_ctx':                 'Bartik IV: Month (Ctx)',
                # Bartik IV — 工作日/周末 (稳健性 13)
                'bartik_wkday_iv_full':                'Bartik IV: Weekday-Weekend (Full)',
                'bartik_wkday_iv_ctx':                 'Bartik IV: Weekday-Weekend (Ctx)',
                # Bartik IV — 专属/共享 (稳健性 14)
                'bartik_excl_iv_full':                 'Bartik IV: Exclusive-Shared (Full)',
                'bartik_excl_iv_ctx':                  'Bartik IV: Exclusive-Shared (Ctx)',
                'bartik_excl_share_exclusive':         'Bartik Share: Exclusive',
                'bartik_excl_share_shared':            'Bartik Share: Shared',
                # Bartik IV — 地理邻近 (稳健性 15)
                'bartik_geoprox_iv_full':              'Bartik IV: Geo-Proximity (Full)',
                'bartik_geoprox_iv_ctx':               'Bartik IV: Geo-Proximity (Ctx)',
                # Bartik IV — 标题出现 (稳健性 16)
                'bartik_title_iv_full':                'Bartik IV: Title-Body (Full)',
                'bartik_title_iv_ctx':                 'Bartik IV: Title-Body (Ctx)',
                # Bartik IV — 关键词多样性 (稳健性 17)
                'bartik_mden_iv_full':                 'Bartik IV: Mention-Density (Full)',
                'bartik_mden_iv_ctx':                  'Bartik IV: Mention-Density (Ctx)',
                # Bartik IV — 关键词密度 (稳健性 18)
                'bartik_mcount_iv_full':               'Bartik IV: Mention-Count (Full)',
                'bartik_mcount_iv_ctx':                'Bartik IV: Mention-Count (Ctx)',
                # Bartik IV — 提及密度 (稳健性 19)
                'bartik_breadth_iv_full':              'Bartik IV: Outlet-Breadth (Full)',
                'bartik_breadth_iv_ctx':               'Bartik IV: Outlet-Breadth (Ctx)',
                # Bartik IV — 银行提及次数 (稳健性 20)
                'bartik_fwdlook_iv_full':              'Bartik IV: Forward-Looking (Full)',
                'bartik_fwdlook_iv_ctx':               'Bartik IV: Forward-Looking (Ctx)',
                # Bartik IV — 媒体覆盖广度 (稳健性 21)
                'bartik_sentlen_iv_full':              'Bartik IV: Sentence-Length (Full)',
                'bartik_sentlen_iv_ctx':               'Bartik IV: Sentence-Length (Ctx)',
                # Bartik IV — 前瞻性语言 (稳健性 22)
                'bartik_ttr_iv_full':                  'Bartik IV: Type-Token-Ratio (Full)',
                'bartik_ttr_iv_ctx':                   'Bartik IV: Type-Token-Ratio (Ctx)',
                # Bartik IV — 平均句长 (稳健性 23)
                'bartik_pubfmt_iv_full':               'Bartik IV: Pub-Format (Full)',
                'bartik_pubfmt_iv_ctx':                'Bartik IV: Pub-Format (Ctx)',
                # Bartik IV — 词汇丰富度 (稳健性 24)
                'bartik_author_iv_full':               'Bartik IV: Author-Byline (Full)',
                'bartik_author_iv_ctx':                'Bartik IV: Author-Byline (Ctx)',
                # Bartik IV — 出版形态 (稳健性 25)
                'bartik_page_iv_full':                 'Bartik IV: Section-Position (Full)',
                'bartik_page_iv_ctx':                  'Bartik IV: Section-Position (Ctx)',
                # Bartik IV — 作者署名 (稳健性 26)
                'bartik_pgnum_iv_full':                'Bartik IV: Page-Number (Full)',
                'bartik_pgnum_iv_ctx':                 'Bartik IV: Page-Number (Ctx)',
                # Bartik IV — 版面位置 (稳健性 27)
                'bartik_kwdiv_iv_full':                'Bartik IV: Keyword-Diversity (Full)',
                'bartik_kwdiv_iv_ctx':                 'Bartik IV: Keyword-Diversity (Ctx)',
                # Bartik IV — 页号位置 (稳健性 28)
                'bartik_kwden_iv_full':                'Bartik IV: Keyword-Density (Full)',
                'bartik_kwden_iv_ctx':                 'Bartik IV: Keyword-Density (Ctx)',
                # Bartik IV — 基期敏感性
                'bartik_type_iv_full_t0':              'Bartik IV: Type (Full, T0)',
                'bartik_type_iv_full_t1':              'Bartik IV: Type (Full, T0+1)',
                'bartik_type_iv_full_t01':             'Bartik IV: Type (Full, T0&T0+1)',
                'bartik_type_iv_ctx_t0':               'Bartik IV: Type (Ctx, T0)',
                'bartik_type_iv_ctx_t1':               'Bartik IV: Type (Ctx, T0+1)',
                'bartik_type_iv_ctx_t01':              'Bartik IV: Type (Ctx, T0&T0+1)',
                # 经济圈 LOO IV
                'zone_leave1out_tone_full':            'Econ Zone Leave-1-Out Tone (Full)',
                'zone_leave1out_tone_ctx':             'Econ Zone Leave-1-Out Tone (Ctx)',
                'bank_zone':                           'Economic Zone',
                # DID 政策冲击
                'dcep_treated':                        'DCEP Pilot (0/1)',
                'dcep_post':                           'Post DCEP Pilot (0/1)',
                'dcep_treat_year':                     'DCEP First Treatment Year',
                'sandbox_treated':                     'Fintech Sandbox (0/1)',
                'sandbox_post':                        'Post Sandbox (0/1)',
                'sandbox_treat_year':                  'Sandbox First Treatment Year',
                # 其他
                'has_coverage':                        'Has News Coverage (0/1)',
            }
            # 仅保留面板中实际存在的列
            labels = {k: v for k, v in STATA_LABELS.items()
                      if k in panel_stata.columns}
            panel_stata.to_stata(dta_path, write_index=False, version=118,
                                 variable_labels=labels)
            logger.info(f"  已导出 Stata 文件: {dta_path}")
        except Exception as e:
            logger.warning(f"  Stata 导出失败: {e}")

    # 文章-银行级数据
    article_filename = FILENAMES.get('output_40_article_bank', '40_article_bank_level.parquet')
    article_path = os.path.join(OUTPUT_DIR, article_filename)
    save_dataset(df_exploded, article_path, logger)


# ============================================================================
# 主流程
# ============================================================================

def main():
    """40_build_panel 主流程。"""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===    40_build_panel: Bank-Year 面板数据构建    ===")
    logger.info("=" * 70)

    # --- 1. 数据加载与验证 ---
    logger.info("=" * 60)
    logger.info("步骤 1: 数据加载与验证")
    logger.info("=" * 60)

    input_filename = FILENAMES.get('output_23_bert_tone', '23_bert_tone.parquet')
    input_path = os.path.join(OUTPUT_DIR, input_filename)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        sys.exit(1)

    df = pd.read_parquet(input_path)
    logger.info(f"  已加载: {input_path}")
    logger.info(f"  行数: {len(df):,}, 列数: {df.shape[1]}")

    # 校验关键列
    required_cols = ['target_bank', 'llm_sentiment_full', '日期', 'llm_agreement_rate_full']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        logger.error(f"  缺失关键列: {missing}")
        sys.exit(1)
    logger.info(f"  关键列校验通过 ✓")

    # --- 2. 篇章级情感数值编码 ---
    df = encode_sentiment(df)

    # --- 3. 多银行特征提取（展开已在阶段 11 完成） ---
    logger.info("=" * 60)
    logger.info("步骤 3: 多银行特征提取（展开已在阶段 11 完成）")
    logger.info("=" * 60)
    logger.info(f"  target_bank 列已存在, 唯一银行数: {df['target_bank'].nunique()}")
    # 计算多银行特征（基于 co_mentioned_banks）
    if 'co_mentioned_banks' in df.columns:
        df['bank_count'] = df['co_mentioned_banks'].apply(
            lambda x: len(str(x).split(';')) + 1 if x and str(x).strip() else 1
        )
    else:
        df['bank_count'] = 1
    df['is_multi_bank'] = (df['bank_count'] > 1).astype(int)
    df['ln_bank_count'] = np.log1p(df['bank_count'])
    # in_title 已在 11_news_bank.py 中作为 target_bank_in_title 生成
    if 'target_bank_in_title' in df.columns:
        df['in_title'] = df['target_bank_in_title'].astype(int)
    elif 'in_title' not in df.columns:
        df['in_title'] = 0

    # --- 3b. 提及密度加权列预计算 (Value-weighted Exposure, Hassan 2019 QJE) ---
    if 'mention_density' in df.columns:
        logger.info("=" * 60)
        logger.info("步骤 3b: 提及密度加权列预计算 (VW, 双轨)")
        logger.info("=" * 60)
        w = df['mention_density'].fillna(0)
        for track in ['_full', '_ctx']:
            # 情感离散/连续
            df[f'llm_vote_score_w{track}'] = df[f'llm_vote_score{track}'] * w
            df[f'llm_vote_cont_w{track}'] = df[f'llm_vote_cont{track}'] * w
            # 频次
            df[f'is_positive_w{track}'] = df[f'is_positive{track}'] * w
            df[f'is_negative_w{track}'] = df[f'is_negative{track}'] * w
            # LLM 逐模型
            for short in LLM_MODELS:
                for sfx in ['_score', '_cont']:
                    src = f'{short}{sfx}{track}'
                    if src in df.columns:
                        df[f'{src}_w'] = df[src] * w
            # 词典
            for d in DICT_NAMES:
                src = f'{d}_score{track}'
                if src in df.columns:
                    df[f'{src}_w'] = df[src] * w
            # 词典 IDF (Gentzkow, Kelly & Taddy 2019, JEL)
            for d in DICT_NAMES:
                src = f'{d}_idf_score{track}'
                if src in df.columns:
                    df[f'{src}_w'] = df[src] * w
            # BERT
            for b in BERT_MODELS:
                for label in ['_正面', '_负面']:
                    src = f'{b}{label}{track}'
                    if src in df.columns:
                        df[f'{src}_w'] = df[src] * w
        vw_cols = [c for c in df.columns if c.endswith('_w')]
        logger.info(f"  已生成 {len(vw_cols)} 个加权列")
    else:
        logger.info("  mention_density 列不存在, 跳过加权列预计算")

    # --- 3c. 媒体权威性加权列预计算 (Holzman et al. 2023, TAR) ---
    if PANEL_CFG.get('compute_media_authority_weighting', False):
        df = compute_media_authority_weights(df)
        mw = df['media_authority_weight'].fillna(1.0)
        for track in ['_full', '_ctx']:
            df[f'llm_vote_score_mw{track}'] = df[f'llm_vote_score{track}'] * mw
            df[f'llm_vote_cont_mw{track}'] = df[f'llm_vote_cont{track}'] * mw
            for short in LLM_MODELS:
                for sfx in ['_score', '_cont']:
                    src = f'{short}{sfx}{track}'
                    if src in df.columns:
                        df[f'{short}{sfx}_mw{track}'] = df[src] * mw
            for d in DICT_NAMES:
                src = f'{d}_score{track}'
                if src in df.columns:
                    df[f'{d}_score_mw{track}'] = df[src] * mw
                src_idf = f'{d}_idf_score{track}'
                if src_idf in df.columns:
                    df[f'{d}_idf_score_mw{track}'] = df[src_idf] * mw
            for b in BERT_MODELS:
                for label in ['_正面', '_负面']:
                    src = f'{b}{label}{track}'
                    if src in df.columns:
                        df[f'{b}{label}_mw{track}'] = df[src] * mw
        mw_cols = [c for c in df.columns if '_mw' in c]
        logger.info(f"  已生成 {len(mw_cols)} 个媒体权威性加权列")

    # --- 4. 时间解析 ---
    df = parse_time(df)

    # 保存展开后文章级数据引用
    df_exploded = df.copy()

    # --- 5. Bank-Year 聚合 ---
    panel = aggregate_panel(df)

    # --- 6. 面板平衡 ---
    panel = balance_panel(panel)

    # --- 6a. has_coverage 哑变量 ---
    panel['has_coverage'] = (panel['n_articles'] > 0).astype(int)
    logger.info(f"  has_coverage: 有报道={panel['has_coverage'].sum()}, "
                f"无报道={len(panel) - panel['has_coverage'].sum()}")

    # --- 6b. 金融科技注意力指数 (三级) ---
    # ⚠️ 必须在 balance_panel() 之后调用 (确保完全笛卡尔积)
    # ⚠️ 不使用 df_exploded (仅含 fintech 文章), 而是直接读取
    #    12_fintech_news_full.parquet (含全量银行新闻)
    if PANEL_CFG.get('compute_attention_index', True):
        panel = compute_fintech_attention_index(panel)

    # --- 6c. 媒体异质性变量 (四维度) ---
    if PANEL_CFG.get('compute_media_heterogeneity', True):
        panel = compute_media_heterogeneity(df_exploded, panel)

    # --- 7. 综合指标 ---
    panel = compute_composite_indicators(panel)

    # --- 7b. 年度截面标准化 ---
    panel = standardize_panel_variables(panel)

    # --- 7c. 银行注册地地理信息 ---
    # 从 bank_addresses.json 合并省份和城市, 用于:
    #   (1) 省级/城市级聚类标准误 (Luo & Li 2025, Table A.2)
    #   (2) 步骤 7d leave-one-out IV 的前置依赖
    panel = merge_bank_geography(panel)

    # --- 7d. Leave-one-out 地理平均情感 (IV) ---
    # 构建同省/同城市其他银行的平均情感 → 工具变量
    # (Luo & Li 2025, Table 3: Province_news_sentiment)
    panel = compute_leave_one_out_sentiment(panel)

    # --- 7e. Bartik IV (29套分类维度) ---
    if PANEL_CFG.get('compute_bartik_iv', True):
        logger.info("=" * 60)
        logger.info("步骤 7e: Bartik Shift-Share IV (29套)")
        logger.info("=" * 60)
        type_map, scale_map = load_bank_group_maps()
        T0 = panel['year'].min()

        # --- 主 Bartik: 银行类型 (6类, 5有效IV) ---
        panel = compute_bartik_iv(panel, df_exploded, type_map, 'type')
        # 基期敏感性 (T0, T0+1, T0&T0+1)
        # ⚠️ 使用 merge-based 赋值，避免 .values 行序错配
        for suffix, base_yr in [('_t0', T0), ('_t1', T0+1)]:
            ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                     df_exploded, type_map, 'type',
                                     base_year=base_yr)
            for track in ['_full', '_ctx']:
                src_col = f'bartik_type_iv{track}'
                dst_col = f'bartik_type_iv{track}{suffix}'
                ptmp = ptmp.rename(columns={src_col: dst_col})
            panel = panel.merge(
                ptmp[['target_bank', 'year',
                      f'bartik_type_iv_full{suffix}',
                      f'bartik_type_iv_ctx{suffix}']],
                on=['target_bank', 'year'], how='left')
        base_t01 = df_exploded[df_exploded['year'].isin([T0, T0+1])]
        ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                 base_t01, type_map, 'type', base_year=T0)
        for track in ['_full', '_ctx']:
            src_col = f'bartik_type_iv{track}'
            ptmp = ptmp.rename(columns={src_col: f'bartik_type_iv{track}_t01'})
        panel = panel.merge(
            ptmp[['target_bank', 'year',
                  'bartik_type_iv_full_t01',
                  'bartik_type_iv_ctx_t01']],
            on=['target_bank', 'year'], how='left')

        # --- 稳健性 1: 银行规模 (4类, 3有效IV) ---
        panel = compute_bartik_iv(panel, df_exploded, scale_map, 'scale')

        # --- 稳健性 2: 金融科技类型 (2类, 1有效IV) ---
        fintech_map = {'底层技术': 'tech', '应用场景': 'app'}
        panel = compute_bartik_iv_fintech(panel, df_exploded, fintech_map, 'fintech')

        # --- 稳健性 3-6: 媒体分类 Bartik (4种分类方式) ---
        # 3=财经/综合 4=中央/地方 5=财经/非财经 6=综合/非综合
        cls_path = os.path.join(os.path.dirname(__file__),
                                'config', 'media_classification.json')
        if os.path.exists(cls_path):
            with open(cls_path, 'r', encoding='utf-8') as f:
                media_cls = json.load(f)
            FIN = set(media_cls.get('financial_media', []))
            COMP = set(media_cls.get('comprehensive_media', []))
            CENTRAL = set(media_cls.get('central_media', []))
            media_col = '媒体(中文)'

            # 3a: 财经/综合/其他
            if '_media_type' not in df_exploded.columns:
                df_exploded['_media_type'] = df_exploded[media_col].apply(
                    lambda x: 'fin' if x in FIN else ('comp' if x in COMP else 'other')
                )
            media_map = {'fin': 'fin', 'comp': 'comp', 'other': 'other'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, media_map, 'media',
                category_col='_media_type'
            )

            # 3b: 中央级/地方级
            df_exploded['_media_central'] = df_exploded[media_col].apply(
                lambda x: 'central' if x in CENTRAL else 'local'
            )
            mcentral_map = {'central': 'central', 'local': 'local'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcentral_map, 'mcentral',
                category_col='_media_central'
            )

            # 3c: 财经/非财经
            df_exploded['_media_fin_binary'] = df_exploded[media_col].apply(
                lambda x: 'fin' if x in FIN else 'nonfin'
            )
            mfin_map = {'fin': 'fin', 'nonfin': 'nonfin'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mfin_map, 'mfin',
                category_col='_media_fin_binary'
            )

            # 3d: 综合性/非综合性
            df_exploded['_media_comp_binary'] = df_exploded[media_col].apply(
                lambda x: 'comp' if x in COMP else 'noncomp'
            )
            mcomp_map = {'comp': 'comp', 'noncomp': 'noncomp'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcomp_map, 'mcomp',
                category_col='_media_comp_binary'
            )

            logger.info(f"  媒体分类 Bartik: 3a(fin/comp/other) + "
                        f"3b(central/local) + 3c(fin/nonfin) + 3d(comp/noncomp)")
        else:
            logger.warning("  media_classification.json 不存在, 跳过所有媒体分类 Bartik")

        # --- 稳健性 7: 媒体省份 ---
        MPROV_MIN_ARTICLES = 5
        mprov_col = '国家地区/省份'
        if mprov_col in df_exploded.columns:
            prov_counts = df_exploded[mprov_col].value_counts()
            valid_provs = set(prov_counts[prov_counts >= MPROV_MIN_ARTICLES].index)
            mprov_map = {p: p for p in valid_provs}
            mprov_map['other'] = 'other'
            df_exploded['_media_province'] = df_exploded[mprov_col].apply(
                lambda x: x if x in valid_provs else 'other'
            )
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mprov_map, 'mprov',
                category_col='_media_province'
            )
            logger.info(f"  媒体省份 Bartik: {len(valid_provs)} 个有效省份")
        else:
            logger.warning(f"  列 '{mprov_col}' 不存在, 跳过媒体省份 Bartik")

        # --- 稳健性 8: 媒体权威性 ---
        mw_path = os.path.join(os.path.dirname(__file__),
                               'config', 'media_weights.json')
        if os.path.exists(mw_path):
            with open(mw_path, 'r', encoding='utf-8') as f:
                mw = json.load(f)
            mw = {k: v for k, v in mw.items() if not k.startswith('//')}
            media_col = '媒体(中文)'
            df_exploded['_media_authority'] = df_exploded[media_col].apply(
                lambda x: 'high' if mw.get(x, 10) >= 80
                          else ('mid' if mw.get(x, 10) >= 60 else 'low')
            )
            mauth_map = {'high': 'high', 'mid': 'mid', 'low': 'low'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mauth_map, 'mauth',
                category_col='_media_authority'
            )
        else:
            logger.warning("  media_weights.json 不存在, 跳过媒体权威性 Bartik")

        # --- 稳健性 9: 文章长度 ---
        if 'doc_length' in df_exploded.columns:
            year_median_doclen = df_exploded.groupby('year')['doc_length'].transform('median')
            df_exploded['_doclen_type'] = np.where(
                df_exploded['doc_length'] > year_median_doclen,
                'long', 'short'
            )
            doclen_map = {'long': 'long', 'short': 'short'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, doclen_map, 'doclen',
                category_col='_doclen_type'
            )
        else:
            logger.warning("  doc_length 列不存在, 跳过文章长度 Bartik")

        # --- 稳健性 10: 半年度 ---
        date_col = '日期'
        if date_col in df_exploded.columns:
            df_exploded['_half_year'] = df_exploded[date_col].apply(
                lambda x: 'H1' if pd.to_datetime(x).month <= 6 else 'H2'
            )
            half_map = {'H1': 'H1', 'H2': 'H2'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, half_map, 'half',
                category_col='_half_year'
            )
        else:
            logger.warning(f"  列 '{date_col}' 不存在, 跳过半年度 Bartik")

        # --- 稳健性 11: 季度 ---
        if date_col in df_exploded.columns:
            df_exploded['_quarter'] = df_exploded[date_col].apply(
                lambda x: f'Q{(pd.to_datetime(x).month - 1) // 3 + 1}'
            )
            qtr_map = {'Q1': 'Q1', 'Q2': 'Q2', 'Q3': 'Q3', 'Q4': 'Q4'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, qtr_map, 'qtr',
                category_col='_quarter'
            )

        # --- 稳健性 12: 月度 ---
        if date_col in df_exploded.columns:
            df_exploded['_pub_month'] = df_exploded[date_col].apply(
                lambda x: f'M{pd.to_datetime(x).month:02d}'
            )
            month_map = {f'M{m:02d}': f'M{m:02d}' for m in range(1, 13)}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, month_map, 'month',
                category_col='_pub_month'
            )

        # --- 稳健性 13: 工作日/周末 ---
        if date_col in df_exploded.columns:
            df_exploded['_wkday_type'] = df_exploded[date_col].apply(
                lambda x: 'weekend' if pd.to_datetime(x).dayofweek >= 5 else 'weekday'
            )
            wkday_map = {'weekday': 'weekday', 'weekend': 'weekend'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, wkday_map, 'wkday',
                category_col='_wkday_type'
            )

        # --- 稳健性 14: 专属/共享报道 ---
        if 'is_multi_bank' in df_exploded.columns:
            df_exploded['_excl_type'] = df_exploded['is_multi_bank'].map(
                {0: 'exclusive', 1: 'shared'}
            )
            excl_map = {'exclusive': 'exclusive', 'shared': 'shared'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, excl_map, 'excl',
                category_col='_excl_type'
            )
        else:
            logger.warning("  is_multi_bank 列不存在, 跳过专属/共享 Bartik")

        # --- 稳健性 15: 地理邻近性 ---
        media_prov_col = '国家地区/省份'
        if media_prov_col in df_exploded.columns:
            addr_path = os.path.join(os.path.dirname(__file__),
                                     'config', 'bank_addresses.json')
            if os.path.exists(addr_path):
                with open(addr_path, 'r', encoding='utf-8') as f:
                    _addr = json.load(f)
                _prov_map = {k: v.get('province', '') for k, v in _addr.items()}
                df_exploded['_bank_prov'] = df_exploded['target_bank'].map(_prov_map)
                df_exploded['_geo_proximity'] = np.where(
                    df_exploded[media_prov_col] == df_exploded['_bank_prov'],
                    'local', 'nonlocal'
                )
                geoprox_map = {'local': 'local', 'nonlocal': 'nonlocal'}
                panel = compute_bartik_iv_fintech(
                    panel, df_exploded, geoprox_map, 'geoprox',
                    category_col='_geo_proximity'
                )

        # --- 稳健性 16: 标题出现 ---
        if 'target_bank_in_title' in df_exploded.columns:
            df_exploded['_title_type'] = df_exploded['target_bank_in_title'].map(
                {1: 'title', 0: 'body'}
            )
            title_map = {'title': 'title', 'body': 'body'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, title_map, 'title',
                category_col='_title_type'
            )

        # --- 稳健性 17: 关键词多样性 ---
        if 'fintech_distinct_keywords' in df_exploded.columns:
            year_median_kwdiv = df_exploded.groupby('year')['fintech_distinct_keywords'].transform('median')
            df_exploded['_kwdiv_type'] = np.where(
                df_exploded['fintech_distinct_keywords'] > year_median_kwdiv,
                'high_div', 'low_div'
            )
            kwdiv_map = {'high_div': 'high_div', 'low_div': 'low_div'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, kwdiv_map, 'kwdiv',
                category_col='_kwdiv_type'
            )

        # --- 稳健性 18: 关键词密度 ---
        if 'fintech_total_count' in df_exploded.columns:
            year_median_kwden = df_exploded.groupby('year')['fintech_total_count'].transform('median')
            df_exploded['_kwden_type'] = np.where(
                df_exploded['fintech_total_count'] > year_median_kwden,
                'dense', 'sparse'
            )
            kwden_map = {'dense': 'dense', 'sparse': 'sparse'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, kwden_map, 'kwden',
                category_col='_kwden_type'
            )

        # --- 稳健性 19: 提及密度 ---
        if 'mention_density' in df_exploded.columns:
            year_median_mden = df_exploded.groupby('year')['mention_density'].transform('median')
            df_exploded['_mden_type'] = np.where(
                df_exploded['mention_density'] > year_median_mden,
                'deep', 'shallow'
            )
            mden_map = {'deep': 'deep', 'shallow': 'shallow'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mden_map, 'mden',
                category_col='_mden_type'
            )

        # --- 稳健性 20: 银行提及次数 ---
        if 'target_bank_mention_count' in df_exploded.columns:
            df_exploded['_mcount_type'] = pd.cut(
                df_exploded['target_bank_mention_count'],
                bins=[-1, 3, 4, float('inf')],  # -1 确保 mention_count=0 也被覆盖
                labels=['low', 'mid', 'high']
            ).astype(str)  # Categorical → str, 避免下游 map() 兼容性问题
            mcount_map = {'low': 'low', 'mid': 'mid', 'high': 'high'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcount_map, 'mcount',
                category_col='_mcount_type'
            )

        # --- 稳健性 21: 媒体覆盖广度 ---
        media_col = '媒体(中文)'
        if media_col in df_exploded.columns:
            media_bank_counts = df_exploded.groupby(media_col)['target_bank'].nunique()
            median_cov = media_bank_counts.median()
            broad_set = set(media_bank_counts[media_bank_counts > median_cov].index)
            df_exploded['_breadth_type'] = df_exploded[media_col].apply(
                lambda m: 'broad' if m in broad_set else 'niche'
            )
            breadth_map = {'broad': 'broad', 'niche': 'niche'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, breadth_map, 'breadth',
                category_col='_breadth_type'
            )

        # --- 稳健性 22: 前瞻性语言 ---
        if 'forward_looking_ratio_full' in df_exploded.columns:
            year_median_fl = df_exploded.groupby('year')['forward_looking_ratio_full'].transform('median')
            df_exploded['_fwdlook_type'] = np.where(
                df_exploded['forward_looking_ratio_full'] > year_median_fl,
                'forward', 'backward'
            )
            fwdlook_map = {'forward': 'forward', 'backward': 'backward'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, fwdlook_map, 'fwdlook',
                category_col='_fwdlook_type'
            )

        # --- 稳健性 23: 平均句长 ---
        if 'avg_sentence_len_full' in df_exploded.columns:
            year_median_sl = df_exploded.groupby('year')['avg_sentence_len_full'].transform('median')
            df_exploded['_sentlen_type'] = np.where(
                df_exploded['avg_sentence_len_full'] > year_median_sl,
                'complex', 'simple'
            )
            sentlen_map = {'complex': 'complex', 'simple': 'simple'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, sentlen_map, 'sentlen',
                category_col='_sentlen_type'
            )

        # --- 稳健性 24: 词汇丰富度 TTR ---
        if 'type_token_ratio_full' in df_exploded.columns:
            year_median_ttr = df_exploded.groupby('year')['type_token_ratio_full'].transform('median')
            df_exploded['_ttr_type'] = np.where(
                df_exploded['type_token_ratio_full'] > year_median_ttr,
                'diverse', 'uniform'
            )
            ttr_map = {'diverse': 'diverse', 'uniform': 'uniform'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, ttr_map, 'ttr',
                category_col='_ttr_type'
            )

        # --- 稳健性 25: 出版形态 ---
        if '媒体类型(中文)' in df_exploded.columns:
            pubfmt_map_raw = {
                '报纸': 'newspaper', '杂志': 'magazine', '新闻通讯社': 'agency'
            }
            df_exploded['_pubformat'] = df_exploded['媒体类型(中文)'].map(pubfmt_map_raw).fillna('newspaper')
            pubfmt_map = {'newspaper': 'newspaper', 'magazine': 'magazine', 'agency': 'agency'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, pubfmt_map, 'pubfmt',
                category_col='_pubformat'
            )

        # --- 稳健性 26: 作者署名 ---
        if '作者' in df_exploded.columns:
            df_exploded['_author_type'] = np.where(
                df_exploded['作者'].notna() & (df_exploded['作者'].astype(str).str.strip() != ''),
                'named', 'anonymous'
            )
            author_map = {'named': 'named', 'anonymous': 'anonymous'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, author_map, 'author',
                category_col='_author_type'
            )

        # --- 稳健性 27: 版面位置 ---
        if '版面' in df_exploded.columns:
            front_page_keywords = ['头版', '要闻', '头条']
            df_exploded['_section_pos'] = np.where(
                df_exploded['版面'].fillna('').str.contains('|'.join(front_page_keywords)),
                'front_page', 'inner'
            )
            page_map = {'front_page': 'front_page', 'inner': 'inner'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, page_map, 'page',
                category_col='_section_pos'
            )

        # --- 稳健性 28: 页号位置 ---
        if '页号' in df_exploded.columns:
            def extract_page_num(x):
                if pd.isna(x):
                    return np.nan
                nums = re.findall(r'\d+', str(x))
                return int(nums[0]) if nums else np.nan
            df_exploded['_page_numeric'] = df_exploded['页号'].apply(extract_page_num)
            df_exploded['_pgnum_type'] = np.where(
                df_exploded['_page_numeric'].fillna(99) <= 3,
                'early_page', 'late_page'
            )
            pgnum_map = {'early_page': 'early_page', 'late_page': 'late_page'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, pgnum_map, 'pgnum',
                category_col='_pgnum_type'
            )

        logger.info(f"  Bartik IV 共29套已完成")

    # --- 7f. 经济圈 Leave-One-Out IV ---
    if PANEL_CFG.get('compute_bartik_iv', True):
        logger.info("=" * 60)
        logger.info("步骤 7f: 经济圈 Leave-One-Out IV")
        logger.info("=" * 60)
        panel = compute_zone_leave1out(panel, df_exploded)

    # --- 7g. DID 政策冲击变量 ---
    if PANEL_CFG.get('compute_policy_shocks', True):
        logger.info("=" * 60)
        logger.info("步骤 7g: DID 政策冲击变量 (DCEP + Sandbox)")
        logger.info("=" * 60)
        panel = merge_policy_shocks(panel)

    log_diagnostics(panel, df_exploded)

    # --- 9. 导出 ---
    export_panel(panel, df_exploded)

    # --- 阶段摘要 ---
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=len(df_exploded),
        output_rows=len(panel),
        extra_info={
            '唯一银行数': panel['target_bank'].nunique(),
            '年份跨度': f"{panel['year'].min()}-{panel['year'].max()}",
            '零新闻观测占比': f"{(panel['n_articles'] == 0).mean():.1%}",
            '面板总列数': panel.shape[1],
            '分类指标': '已生成' if 'n_articles_tech' in panel.columns else '未生成',
        }
    )

    logger.info("40_build_panel 执行完毕 ✓")


if __name__ == '__main__':
    main()
