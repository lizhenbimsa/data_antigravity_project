"""
46_network_spillovers.py — 同行网络传染/溢出效应模块
==========================================================

功能:
  从 co_mentioned_banks 构建银行共现邻接矩阵,
  行随机标准化后, 用 Lag(Y-1) 加权平均同行情感作为网络压力变量,
  合并至年度面板。

学术依据:
  - Leary & Roberts (2014, JF): 同行效应与公司金融决策
  - Manski (1993, RES): 反射问题 → 使用 Lag(Y-1) 规避
  - 行随机标准化: 防止大银行规模主导网络权重

关键设计:
  - 邻接矩阵: A[i,j] = bank_i 与 bank_j 在 Year t 的新闻共现次数
  - 行随机标准化: W[i,j] = A[i,j] / Σ_k A[i,k], 每行和为 1
  - 网络压力: peer_tone_i,t = Σ_j W[i,t-1] × tone_j,t-1
  - 严格 Lag(Y-1): 用去年的网络权重 × 去年的同行情感

输入: 41_panel_encode_aggregate 生成的面板 + 篇章级 df_exploded
输出: 面板中追加 peer_tone_lag1_* 列
"""

import logging
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix, lil_matrix

from utils.helpers import load_config, setup_logging

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "46_network_spillovers"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 邻接矩阵构建
# ============================================================================

def build_adjacency_matrix(
    df_exploded: pd.DataFrame, 
    year: int
) -> tuple[pd.DataFrame, list[str]]:
    """从篇章级数据构建特定年份的银行共现邻接矩阵。

    Args:
        df_exploded: 篇章级 DataFrame, 须含 'target_bank', 'co_mentioned_banks', 'year'
        year: 目标年份

    Returns:
        (adj_df, bank_list): 邻接矩阵 DataFrame 和银行列表
    """
    df_year = df_exploded[df_exploded['year'] == year].copy()

    if df_year.empty:
        return pd.DataFrame(), []

    # 获取所有银行
    all_banks = sorted(df_year['target_bank'].unique())
    bank_to_idx = {b: i for i, b in enumerate(all_banks)}
    n = len(all_banks)

    if n < 2:
        return pd.DataFrame(), all_banks

    # 构建稀疏邻接矩阵
    adj = lil_matrix((n, n), dtype=np.float64)

    for _, row in df_year.iterrows():
        target = row['target_bank']
        co_banks_raw = row.get('co_mentioned_banks', '')

        if pd.isna(co_banks_raw) or str(co_banks_raw).strip() == '':
            continue

        # co_mentioned_banks 是分号分隔的字符串
        co_banks = [b.strip() for b in str(co_banks_raw).split(';') if b.strip()]

        i = bank_to_idx.get(target)
        if i is None:
            continue

        for co_bank in co_banks:
            j = bank_to_idx.get(co_bank)
            if j is not None and i != j:  # 排除自环
                adj[i, j] += 1
                adj[j, i] += 1  # 对称

    adj_csr = adj.tocsr()
    adj_df = pd.DataFrame(adj_csr.toarray(), index=all_banks, columns=all_banks)
    return adj_df, all_banks


# ============================================================================
# 3. 行随机标准化
# ============================================================================

def row_stochastic_normalize(adj_df: pd.DataFrame) -> pd.DataFrame:
    """行随机标准化: 每行除以行和, 使得每行权重总和为 1。

    这确保了大银行对其他银行施加的"总压力"与小银行相同 (均为 100%),
    防止了规模效应导致的内生性偏误。

    Args:
        adj_df: 对称邻接矩阵 DataFrame

    Returns:
        row_norm: 行随机标准化后的权重矩阵
    """
    row_sums = adj_df.sum(axis=1)
    # 防止除零: 无共现的银行保持全零行
    row_sums = row_sums.replace(0, np.nan)
    row_norm = adj_df.div(row_sums, axis=0).fillna(0)
    return row_norm


# ============================================================================
# 4. 网络溢出变量计算
# ============================================================================

def compute_network_spillovers(
    panel: pd.DataFrame, 
    df_exploded: pd.DataFrame
) -> pd.DataFrame:
    """计算同行网络传染变量并合并至面板。

    核心逻辑:
      peer_tone_i,t = Σ_j W[i,t-1] × tone_j,t-1
      即: 用去年的网络权重 × 去年的同行情感

    Args:
        panel: Bank-Year 面板 DataFrame
        df_exploded: 篇章级 DataFrame

    Returns:
        panel: 追加 peer_tone_lag1_* 列的面板
    """
    logger.info("=" * 60)
    logger.info("步骤: 同行网络传染/溢出效应计算")
    logger.info("=" * 60)

    if 'co_mentioned_banks' not in df_exploded.columns:
        logger.warning("  co_mentioned_banks 列不存在, 跳过网络溢出计算")
        return panel

    # 确保年份列
    if 'year' not in df_exploded.columns:
        logger.warning("  year 列不存在, 跳过网络溢出计算")
        return panel

    years = sorted(panel['year'].unique())
    logger.info(f"  面板年份范围: {min(years)}-{max(years)}, 共 {len(years)} 年")

    # 情感列: 使用 llm_vote_tone_full 作为核心情感指标
    tone_cols = []
    for track in ['_full', '_ctx', '_title']:
        col = f'llm_vote_tone{track}'
        if col in panel.columns:
            tone_cols.append(col)
    
    if not tone_cols:
        logger.warning("  无可用情感列, 跳过网络溢出计算")
        return panel

    logger.info(f"  使用情感列: {tone_cols}")

    # 逐年计算 — 用字典避免多 tone_col 合并丢失
    peer_dict = {}  # key: (bank, year), value: {col_name: value}

    for year in years:
        lag_year = year - 1

        # Lag(Y-1) 的邻接矩阵
        adj_df, bank_list = build_adjacency_matrix(df_exploded, lag_year)

        if adj_df.empty or len(bank_list) < 2:
            logger.info(f"  年份 {year}: 滞后年 {lag_year} 无足够共现数据, 跳过")
            continue

        # 行随机标准化
        W = row_stochastic_normalize(adj_df)

        # 获取 Lag(Y-1) 的面板情感数据
        panel_lag = panel[panel['year'] == lag_year].set_index('target_bank')

        for tone_col in tone_cols:
            # 构建同行情感向量 (对齐到邻接矩阵的银行列表)
            tone_vec = pd.Series(np.nan, index=bank_list)
            for bank in bank_list:
                if bank in panel_lag.index and tone_col in panel_lag.columns:
                    val = panel_lag.loc[bank, tone_col]
                    if isinstance(val, pd.Series):
                        val = val.iloc[0]
                    tone_vec[bank] = val

            # 网络加权: peer_tone = W × tone_vec
            # W: (n×n), tone_vec: (n,) → peer_tone: (n,)
            peer_tone = W.values @ tone_vec.fillna(0).values

            # 存储结果（使用字典累积, 避免多 tone_col 合并丢失）
            suffix = tone_col.replace('llm_vote_tone', '')
            for idx, bank in enumerate(bank_list):
                key = (bank, year)
                if key not in peer_dict:
                    peer_dict[key] = {'target_bank': bank, 'year': year}
                peer_dict[key][f'peer_tone_lag1{suffix}'] = peer_tone[idx]

        n_edges = (adj_df > 0).sum().sum() // 2
        logger.info(f"  年份 {year}: {len(bank_list)} 家银行, "
                    f"{n_edges} 条共现边 (基于 {lag_year} 年数据)")

    # 合并至面板
    if peer_dict:
        peer_df = pd.DataFrame(list(peer_dict.values()))
        
        panel = panel.merge(peer_df, on=['target_bank', 'year'], how='left')
        
        n_filled = len(peer_df)
        logger.info(f"  网络溢出变量已合并: {n_filled:,} 个 Bank-Year 有效值")
        
        # 统计汇总
        for tone_col in tone_cols:
            suffix = tone_col.replace('llm_vote_tone', '')
            peer_col = f'peer_tone_lag1{suffix}'
            if peer_col in panel.columns:
                valid = panel[peer_col].notna().sum()
                logger.info(f"    {peer_col}: {valid:,} 有效值, "
                            f"mean={panel[peer_col].mean():.4f}")
    else:
        logger.warning("  未生成任何网络溢出变量")

    return panel
