"""
46_network_spillovers.py — 同行网络传染/溢出效应模块
==========================================================

管线位置:
  45_panel_export_main.py → 步骤 7f / 7g / 7h-cogn
  本模块在 44_panel_iv_did.py 之后、 47_network_brokerage.py 之前执行。
  依赖 41_panel_encode_aggregate.py 生成的 co_mentioned_banks 列
  和 llm_vote_tone_* 情感指标。

核心功能 (三大子模块):
  1. 同行网络溢出 (compute_network_spillovers):
     从 co_mentioned_banks 构建银行共现邻接矩阵,
     行随机标准化后, 用 Lag(Y-1) 加权平均同行情感作为网络压力变量。
     包含一阶溢出 (W×tone) 和二阶溢出 (W²×tone)。
  2. 银行共现网络中心度 (compute_bank_network_centrality):
     计算 22 种网络中心度指标 (18 节点级 + 4 网络级)。
  3. 认知邻近度 (compute_cognitive_proximity):
     基于 TF-IDF 文本向量余弦相似度衡量银行间知识基础的相似程度。

学术依据:
  Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect
  corporate financial policy? The Journal of Finance, 69(1), 139-178.
  https://doi.org/10.1111/jofi.12094
  → 同行效应与公司金融决策; 本项目用新闻共现构建同行网络

  Manski, C. F. (1993). Identification of endogenous social effects.
  The Review of Economic Studies, 60(3), 531-542. DOI: 10.2307/2298123
  → 反射问题 → 使用 Lag(Y-1) 规避同期内生性

  Boschma, R. (2005). Proximity and innovation: A critical assessment.
  Regional Studies, 39(1), 61-74. DOI: 10.1080/0034340052000320887
  → 认知邻近度的理论基础 (五维邻近度框架)

关键设计:
  - 邻接矩阵: A[i,j] = bank_i 与 bank_j 在 Year t 的新闻共现次数
  - 行随机标准化: W[i,j] = A[i,j] / Σ_k A[i,k], 每行和为 1
    防止大银行规模主导网络权重 (类比空间计量的空间权重矩阵)
  - 网络压力: peer_tone_i,t = Σ_j W[i,t-1] × tone_j,t-1
  - 严格 Lag(Y-1): 用去年的网络权重 × 去年的同行情感
    避免 Manski 反射问题和同期反向因果

输入: 41_panel_encode_aggregate 生成的面板 + 篇章级 df_exploded
输出: 面板中追加 peer_tone_lag1_*、22 种中心度、bank_cogn_mean 列
"""

import logging
import os
import sys
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix, lil_matrix

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as _cosine_sim
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

# Phase 5c-1: 注入项目根, 让 ``news_process.core.*`` 在包模式下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "46_network_spillovers"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 邻接矩阵构建
# ============================================================================
# co_mentioned_banks 列由 11_news_bank.py 在实体匹配阶段生成,
# 格式为分号分隔字符串, 如 "工商银行;建设银行;农业银行"。
# 该矩阵是后续所有网络指标 (溢出、中心度) 的共同基础。

def build_adjacency_matrix(
    df_exploded: pd.DataFrame, 
    year: int
) -> tuple[pd.DataFrame, list[str]]:
    """构建年度银行共现邻接矩阵。

    从 co_mentioned_banks 列解析共现关系:
      如果文章 k 同时提及银行 A 和银行 B,
      则 A[A,B] += 1, A[B,A] += 1 (对称)。

    注: 由此矩阵计算的 bank_degree_cent (Freeman 1979 度中心度)
    在传染病扩散框架中等价于 Dahlke et al. (2024, RP) 的 degree_ai,
    即银行在金融科技信息网络中的连接程度。

    Args:
        df_exploded: 篇章级 DataFrame, 须含 co_mentioned_banks 列
        year: 目标年份

    Returns:
        adj_df: 对称邻接矩阵 DataFrame (index=columns=银行列表)
        bank_list: 银行名称列表
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
# 空间计量经济学标准操作: 将邻接矩阵 A 转化为权重矩阵 W,
# 使每行之和为 1, 从而 W×tone 的含义为"加权平均同行情感"。
# 参考: LeSage, J., & Pace, R. K. (2009). Introduction to Spatial
# Econometrics. CRC Press. DOI: 10.1201/9781420064254

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

            # 二阶溢出: 捕获"邻居的邻居"间接情感传染 (LeSage & Pace 2009)
            # peer_tone_2nd = W × peer_tone = W² × tone
            peer_tone_2nd = W.values @ peer_tone

            # 存储结果（使用字典累积, 避免多 tone_col 合并丢失）
            suffix = tone_col.replace('llm_vote_tone', '')
            for idx, bank in enumerate(bank_list):
                key = (bank, year)
                if key not in peer_dict:
                    peer_dict[key] = {'target_bank': bank, 'year': year}
                peer_dict[key][f'peer_tone_lag1{suffix}'] = peer_tone[idx]
                peer_dict[key][f'peer_tone_2nd_lag1{suffix}'] = peer_tone_2nd[idx]

        # ── 同行金融科技声量溢出 ──
        # Berger, A. N., Guedhami, O., Kim, H. H., & Li, X. (2022).
        # Economic policy uncertainty and bank liquidity hoarding.
        # Journal of Financial Intermediation, 49, 100893.
        # DOI: 10.1016/j.jfi.2020.100893
        # → 同行溢出: peer_fintech_exposure_i,t = Σ_j W[i,t-1] × ln_coverage_j,t-1
        # peer_fintech_exposure_i,t = Σ_j W[i,t-1] × ln_news_coverage_j,t-1
        if 'ln_news_coverage' in panel_lag.columns:
            cov_vec = pd.Series(np.nan, index=bank_list)
            for bank in bank_list:
                if bank in panel_lag.index:
                    val = panel_lag.loc[bank, 'ln_news_coverage']
                    if isinstance(val, pd.Series):
                        val = val.iloc[0]
                    cov_vec[bank] = val
            peer_cov = W.values @ cov_vec.fillna(0).values
            for idx_b, bank in enumerate(bank_list):
                key = (bank, year)
                if key not in peer_dict:
                    peer_dict[key] = {'target_bank': bank, 'year': year}
                peer_dict[key]['peer_fintech_exposure_lag1'] = peer_cov[idx_b]

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
            for prefix in ['peer_tone_lag1', 'peer_tone_2nd_lag1']:
                peer_col = f'{prefix}{suffix}'
                if peer_col in panel.columns:
                    valid = panel[peer_col].notna().sum()
                    logger.info(f"    {peer_col}: {valid:,} 有效值, "
                                f"mean={panel[peer_col].mean():.4f}")
    else:
        logger.warning("  未生成任何网络溢出变量")

    return panel


# ============================================================================
# 5. 银行共现网络中心度计算 (22 指标)
# ============================================================================
# 学术依据:
#   Freeman, L. C. (1979). Centrality in social networks. Social Networks,
#   1(3), 215-239. DOI: 10.1016/0378-8733(78)90021-7
#   → degree, betweenness, closeness 的经典定义
#
#   Burt, R. S. (1992). Structural Holes. Harvard University Press.
#   → constraint, effective_size, ci (结构洞指标)
#
#   Billio, M., et al. (2012). Econometric measures of connectedness
#   and systemic risk. JFE, 104(3), 535-559.
#   DOI: 10.1016/j.jfineco.2011.12.010
#   → 网络密度与系统性风险的理论基础
#
# 设计要点:
#   - 路径型指标 (betweenness/harmonic/closeness/eccentricity) 使用
#     倒数权重图 G_inv (edge_weight = 1/w), 将"共现强度"转为"距离"
#   - CFB 使用原始图 (电导语义), eigenvector 三级 fallback
#   - 断连图: CFB/eccentricity/avg_path 仅对最大连通分量计算
#   - Part C (4 种网络级控制变量) 为年度级, 广播至所有银行

def _gini(arr: np.ndarray) -> float:
    """计算 Gini 系数 (度分布不平等度)。"""
    arr = np.sort(arr)
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return np.nan
    index = np.arange(1, n + 1)
    return (2 * (index * arr).sum() / (n * arr.sum())) - (n + 1) / n


def compute_bank_network_centrality(
    panel: pd.DataFrame,
    df_exploded: pd.DataFrame
) -> pd.DataFrame:
    """计算银行共现网络中心度指标 (22 种) 并合并至面板。

    指标分 4 组:
      Part A (11): degree, strength, betweenness, harmonic, eigen, katz,
                   subgraph, cfbetween, clustering, constraint, hub
      Part B (7):  ego_density, ci, effective_size, closeness,
                   eccentricity, avg_nbr_deg, coreness
      Part C (4):  net_density_yr, net_avg_cluster_yr, net_avg_path_yr,
                   net_degree_gini_yr

    学术依据:
      Freeman (1979), Bonacich (1972), Burt (1992), Estrada (2005),
      Newman (2005), Billio et al. (2012, JFE), Watts & Strogatz (1998)

    关键设计:
      - 路径型指标 (betweenness/harmonic/closeness/eccentricity) 使用
        倒数权重图 G_inv (edge_weight = 1/w)
      - CFB 使用原始图 (weight = 电导语义)
      - eigenvector 三级 fallback: 全图 power → numpy(LCC) → NaN
      - 断连图: CFB/eccentricity/avg_path 仅对最大连通分量计算

    Args:
        panel: Bank-Year 面板 DataFrame
        df_exploded: 篇章级 DataFrame

    Returns:
        panel: 追加 22 列的面板 (18 节点级 + 4 网络级)
    """
    if not HAS_NETWORKX:
        logger.warning("  networkx 未安装, 跳过网络中心度计算。"
                       " 请运行: pip install networkx")
        return panel

    logger.info("=" * 60)
    logger.info("步骤: 银行共现网络中心度计算 (22 指标)")
    logger.info("=" * 60)

    years = sorted(panel['year'].unique())
    logger.info(f"  面板年份范围: {min(years)}-{max(years)}, 共 {len(years)} 年")

    # 结果容器
    node_results = {}   # {(bank, year): {metric: value}}
    net_results = {}    # {year: {metric: value}}

    for year in years:
        # 1. 构建年度邻接矩阵
        adj_df, bank_list = build_adjacency_matrix(df_exploded, year)

        if adj_df.empty or len(bank_list) < 2:
            logger.info(f"  年份 {year}: 共现数据不足, 跳过")
            continue

        n_nodes = len(bank_list)
        n_edges_raw = int((adj_df > 0).sum().sum() // 2)

        # 2. 构建原始图 (用于谱/结构型指标)
        G = nx.Graph()
        for i, b1 in enumerate(bank_list):
            for j, b2 in enumerate(bank_list):
                if j > i and adj_df.iloc[i, j] > 0:
                    G.add_edge(b1, b2, weight=float(adj_df.iloc[i, j]))
        # 确保所有银行都在图中 (含孤立节点)
        for b in bank_list:
            if b not in G:
                G.add_node(b)

        # 3. 构建倒数图 (用于路径型指标: weight = distance)
        G_inv = nx.Graph()
        for u, v, d in G.edges(data=True):
            G_inv.add_edge(u, v, weight=1.0 / d['weight'])
        for b in bank_list:
            if b not in G_inv:
                G_inv.add_node(b)

        # 4. 识别最大连通分量 (用于 CFB, eccentricity, avg_path)
        components = list(nx.connected_components(G))
        lcc_nodes = max(components, key=len) if components else set()
        G_lcc = G.subgraph(lcc_nodes).copy()
        G_inv_lcc = G_inv.subgraph(lcc_nodes).copy()

        # ─── 5. 计算 18 种节点级指标 ───

        metrics = {b: {} for b in bank_list}

        # ── a. 原始图组 (12 种) ──

        # (1) Degree Centrality — 纯拓扑
        dc = nx.degree_centrality(G)
        for b in bank_list:
            metrics[b]['bank_degree_cent'] = dc.get(b, 0.0)

        # (2) Strength Centrality — 加权度, max-normalize
        strength = dict(G.degree(weight='weight'))
        max_str = max(strength.values()) if strength else 1.0
        if max_str == 0:
            max_str = 1.0
        for b in bank_list:
            metrics[b]['bank_strength_cent'] = strength.get(b, 0.0) / max_str

        # (5) Eigenvector Centrality — 三级 fallback
        eigen_done = False
        try:
            ec = nx.eigenvector_centrality(
                G, weight='weight', max_iter=1000, tol=1e-06)
            for b in bank_list:
                metrics[b]['bank_eigen_cent'] = ec.get(b, 0.0)
            eigen_done = True
        except nx.PowerIterationFailedConvergence:
            pass
        if not eigen_done:
            try:
                ec_lcc = nx.eigenvector_centrality_numpy(
                    G_lcc, weight='weight')
                for b in bank_list:
                    metrics[b]['bank_eigen_cent'] = ec_lcc.get(b, np.nan)
                eigen_done = True
            except Exception:
                pass
        if not eigen_done:
            for b in bank_list:
                metrics[b]['bank_eigen_cent'] = np.nan
            logger.warning(f"  年份 {year}: eigenvector 三级 fallback 均失败")

        # (6) Katz Centrality — α = 0.9 / λ_max
        try:
            A = nx.to_numpy_array(G, nodelist=bank_list)
            lam_max = max(abs(np.linalg.eigvals(A)))
            alpha_katz = 0.9 / lam_max if lam_max > 0 else 0.01
            kc = nx.katz_centrality(G, alpha=alpha_katz, weight='weight')
            for b in bank_list:
                metrics[b]['bank_katz_cent'] = kc.get(b, 0.0)
        except Exception as e:
            logger.warning(f"  年份 {year}: Katz 失败 ({e})")
            for b in bank_list:
                metrics[b]['bank_katz_cent'] = np.nan

        # (7) Subgraph Centrality — 不接受 weight, try/except 防溢出
        try:
            sc = nx.subgraph_centrality(G)
            for b in bank_list:
                metrics[b]['bank_subgraph_cent'] = sc.get(b, np.nan)
        except (OverflowError, ValueError, np.linalg.LinAlgError) as e:
            logger.warning(f"  年份 {year}: subgraph_centrality 溢出 ({e})")
            for b in bank_list:
                metrics[b]['bank_subgraph_cent'] = np.nan

        # (8) Current-Flow Betweenness — 原始图, 仅 LCC
        if len(lcc_nodes) >= 2:
            try:
                cfb = nx.current_flow_betweenness_centrality(
                    G_lcc, weight='weight')
                for b in bank_list:
                    metrics[b]['bank_cfbetween_cent'] = cfb.get(b, np.nan)
            except Exception as e:
                logger.warning(f"  年份 {year}: CFB 失败 ({e})")
                for b in bank_list:
                    metrics[b]['bank_cfbetween_cent'] = np.nan
        else:
            for b in bank_list:
                metrics[b]['bank_cfbetween_cent'] = np.nan

        # (9) Clustering Coefficient — 原始图
        cc = nx.clustering(G, weight='weight')
        for b in bank_list:
            metrics[b]['bank_clustering'] = cc.get(b, 0.0)

        # (10) Structural Constraint — 原始图, degree<2 → NaN
        try:
            con = nx.constraint(G, weight='weight')
            for b in bank_list:
                deg = G.degree(b)
                if deg < 2:
                    metrics[b]['bank_constraint'] = np.nan
                else:
                    metrics[b]['bank_constraint'] = con.get(b, np.nan)
        except Exception:
            for b in bank_list:
                metrics[b]['bank_constraint'] = np.nan

        # (12) Ego-Network Density — 手工计算邻居间边密度
        for b in bank_list:
            nbrs = list(G.neighbors(b))
            k = len(nbrs)
            if k <= 1:
                metrics[b]['bank_ego_density'] = np.nan
            else:
                ego_edges = 0
                for ii in range(k):
                    for jj in range(ii + 1, k):
                        if G.has_edge(nbrs[ii], nbrs[jj]):
                            ego_edges += 1
                max_ego = k * (k - 1) / 2
                metrics[b]['bank_ego_density'] = ego_edges / max_ego

        # (14) Effective Size — 原始图
        try:
            es = nx.effective_size(G, weight='weight')
            for b in bank_list:
                if G.degree(b) == 0:
                    metrics[b]['bank_effective_size'] = np.nan
                else:
                    metrics[b]['bank_effective_size'] = es.get(b, np.nan)
        except Exception:
            for b in bank_list:
                metrics[b]['bank_effective_size'] = np.nan

        # (17) Average Neighbor Degree — 原始图, degree=0 → NaN
        and_map = nx.average_neighbor_degree(G, weight='weight')
        for b in bank_list:
            if G.degree(b) == 0:
                metrics[b]['bank_avg_nbr_deg'] = np.nan
            else:
                metrics[b]['bank_avg_nbr_deg'] = and_map.get(b, np.nan)

        # (18) Coreness (k-core) — 纯拓扑
        cn = nx.core_number(G)
        for b in bank_list:
            metrics[b]['bank_coreness'] = cn.get(b, 0)

        # ── b. 倒数图组 (4 种) ──

        # (3) Betweenness Centrality — 倒数图
        bc = nx.betweenness_centrality(G_inv, weight='weight')
        for b in bank_list:
            metrics[b]['bank_between_cent'] = bc.get(b, 0.0)

        # (4) Harmonic Centrality — 倒数图, 参数名 distance
        hc = nx.harmonic_centrality(G_inv, distance='weight')
        for b in bank_list:
            metrics[b]['bank_harmonic_cent'] = hc.get(b, 0.0)

        # (15) Closeness Centrality — 倒数图, 参数名 distance
        clc = nx.closeness_centrality(G_inv, distance='weight')
        for b in bank_list:
            metrics[b]['bank_closeness_cent'] = clc.get(b, 0.0)

        # (16) Eccentricity — 倒数图, 仅 LCC
        if len(lcc_nodes) >= 2:
            try:
                ecc = nx.eccentricity(G_inv_lcc, weight='weight')
                for b in bank_list:
                    metrics[b]['bank_eccentricity'] = ecc.get(b, np.nan)
            except nx.NetworkXError:
                for b in bank_list:
                    metrics[b]['bank_eccentricity'] = np.nan
        else:
            for b in bank_list:
                metrics[b]['bank_eccentricity'] = np.nan

        # ── c. 衍生组 (2 种) ──

        # (13) CI = 1 / constraint
        for b in bank_list:
            c_val = metrics[b].get('bank_constraint', np.nan)
            if pd.notna(c_val) and c_val > 0:
                metrics[b]['bank_ci'] = 1.0 / c_val
            else:
                metrics[b]['bank_ci'] = np.nan

        # (11) Hub (Top 10% degree)
        deg_values = [(b, metrics[b]['bank_degree_cent']) for b in bank_list]
        deg_values.sort(key=lambda x: x[1], reverse=True)
        top10_count = max(1, int(len(deg_values) * 0.10))
        top10_banks = {b for b, _ in deg_values[:top10_count]}
        for b in bank_list:
            metrics[b]['bank_is_hub'] = 1 if b in top10_banks else 0

        # 存储节点级结果
        for b in bank_list:
            node_results[(b, year)] = metrics[b]

        # ─── 6. 网络级控制变量 (Part C) ───

        net_yr = {}

        # N1. 网络密度
        net_yr['net_density_yr'] = nx.density(G)

        # N2. 平均聚类系数
        net_yr['net_avg_cluster_yr'] = nx.average_clustering(
            G, weight='weight')

        # N3. 平均路径长度 (LCC, 倒数图)
        if len(lcc_nodes) >= 2:
            try:
                net_yr['net_avg_path_yr'] = \
                    nx.average_shortest_path_length(
                        G_inv_lcc, weight='weight')
            except nx.NetworkXError:
                net_yr['net_avg_path_yr'] = np.nan
        else:
            net_yr['net_avg_path_yr'] = np.nan

        # N4. 度分布 Gini 系数
        degree_seq = np.array([G.degree(b) for b in bank_list],
                              dtype=np.float64)
        net_yr['net_degree_gini_yr'] = _gini(degree_seq)

        net_results[year] = net_yr

        logger.info(f"  年份 {year}: {n_nodes} 节点, {n_edges_raw} 边, "
                    f"LCC={len(lcc_nodes)}, "
                    f"density={net_yr['net_density_yr']:.4f}")

    # ─── 7. 合并至面板 ───

    if not node_results:
        logger.warning("  未计算任何中心度指标")
        return panel

    # 节点级 → DataFrame
    node_records = []
    for (bank, year), mdict in node_results.items():
        row = {'target_bank': bank, 'year': year}
        row.update(mdict)
        node_records.append(row)
    node_df = pd.DataFrame(node_records)

    # 网络级 → DataFrame (年度级, 广播到所有银行)
    net_records = []
    for year, ndict in net_results.items():
        row = {'year': year}
        row.update(ndict)
        net_records.append(row)
    net_df = pd.DataFrame(net_records)

    # 合并
    panel = panel.merge(node_df, on=['target_bank', 'year'], how='left')
    panel = panel.merge(net_df, on='year', how='left')

    # 统计汇总
    cent_cols = [c for c in node_df.columns
                 if c not in ('target_bank', 'year')]
    net_cols = [c for c in net_df.columns if c != 'year']
    logger.info(f"  网络中心度已合并: {len(cent_cols)} 节点级 + "
                f"{len(net_cols)} 网络级 = {len(cent_cols)+len(net_cols)} 变量")
    for col in cent_cols + net_cols:
        if col in panel.columns:
            valid = panel[col].notna().sum()
            total = len(panel)
            logger.info(f"    {col}: {valid:,}/{total:,} "
                        f"({valid/total:.1%}), "
                        f"mean={panel[col].mean():.4f}")

    return panel


# ============================================================================
# 6. 认知邻近度 (独立顶层函数)
# ============================================================================
# 认知邻近度衡量银行间"知识基础的相似程度":
# - 将每家银行当年所有新闻文本拼接为"超级文档"
# - 使用 TF-IDF 向量化 + Cosine Similarity 计算成对相似度
# - bank_cogn_mean = 银行 i 与所有其他银行的 cosine 均值
# 高值: 银行新闻主题与行业整体高度相似 (认知锁定风险)
# 低值: 银行在信息空间中具有独特性 (差异化优势)
#
# Stata 回归示例:
#   reg Y X bank_cogn_mean, cluster(province)
#   → 控制银行间信息环境的同质性对情感指标的干扰

def compute_cognitive_proximity(
    df_exploded: pd.DataFrame,
    panel: pd.DataFrame
) -> pd.DataFrame:
    """计算银行间认知邻近度 (TF-IDF 文本向量余弦相似度)。

    理论基础:
      Boschma, R. (2005). Proximity and innovation: A critical
      assessment. Regional Studies, 39(1), 61-74.
      DOI: 10.1080/0034340052000320887
      → 认知邻近度 = 知识基础的相似度, Cosine Similarity 为标准操作化

    操作化:
      Dahlke, J., et al. (2024). Epidemic effects in the diffusion
      of emerging digital technologies. Research Policy, 53(2), 104917.
      DOI: 10.1016/j.respol.2023.104917
      → cogn_mean: 每家银行与所有其他银行的 TF-IDF cosine 均值

    设计决策:
      - 逐年计算 (避免跨年词汇漂移)
      - 标题+内容拼接 (信息量最大化)
      - char_wb analyzer + ngram(2,4) (中文友好, 无需分词)
      - 100 字符阈值 (过短文本 TF-IDF 退化)
      - 稀疏矩阵 cosine_similarity (内存安全)

    Args:
        df_exploded: 篇章级 DataFrame, 须含 '内容' 列
        panel: Bank-Year 面板 DataFrame

    Returns:
        panel: 追加 bank_cogn_mean 列的面板
    """
    if not HAS_SKLEARN:
        logger.warning("  scikit-learn 未安装, 跳过认知邻近度计算。"
                       " 请运行: pip install scikit-learn")
        return panel

    logger.info("=" * 60)
    logger.info("步骤: 认知邻近度计算 (Boschma 2005; Dahlke et al. 2024)")
    logger.info("=" * 60)

    # 文本列发现 (复用 24_herd_decay_processor.py L86-87 逻辑)
    text_col = ('内容' if '内容' in df_exploded.columns else
                '正文' if '正文' in df_exploded.columns else 'content')
    title_col = '标题' if '标题' in df_exploded.columns else None

    if text_col not in df_exploded.columns:
        logger.warning(f"  文本列 '{text_col}' 不存在, 跳过认知邻近度")
        return panel

    logger.info(f"  文本列: {text_col}" +
                (f" + {title_col}" if title_col else ""))

    years = sorted(panel['year'].unique())
    cogn_results = {}  # {(bank, year): cogn_mean}

    for year in years:
        df_year = df_exploded[df_exploded['year'] == year]
        if df_year.empty:
            continue

        # 按银行聚合: 标题+内容拼接为"超级文档"
        def _concat_text(group):
            bodies = group[text_col].fillna('').astype(str)
            if title_col and title_col in group.columns:
                titles = group[title_col].fillna('').astype(str)
                return ' '.join(titles + ' ' + bodies)
            return ' '.join(bodies)

        bank_texts = df_year.groupby('target_bank').apply(
            _concat_text, include_groups=False)
        bank_list = bank_texts.index.tolist()
        n_banks = len(bank_list)

        if n_banks < 2:
            continue

        # 100 字符阈值守卫 (≈50 中文词)
        char_counts = bank_texts.str.len()
        valid_mask = char_counts >= 100
        valid_banks = bank_texts[valid_mask]

        if len(valid_banks) < 2:
            for bank in bank_list:
                cogn_results[(bank, year)] = np.nan
            logger.info(f"  年份 {year}: 有效银行 < 2, 全部 NaN")
            continue

        # TF-IDF (复用 24 模块参数)
        try:
            vectorizer = TfidfVectorizer(
                max_features=5000,
                min_df=min(2, len(valid_banks)),
                max_df=0.95,
                analyzer='char_wb',
                ngram_range=(2, 4),
                dtype=np.float32
            )
            tfidf_matrix = vectorizer.fit_transform(valid_banks.values)
        except ValueError as e:
            logger.warning(f"  年份 {year}: TF-IDF 失败 ({e})")
            for bank in bank_list:
                cogn_results[(bank, year)] = np.nan
            continue

        # Cosine similarity (稀疏输入 → dense 输出)
        sim_matrix = _cosine_sim(tfidf_matrix)
        np.fill_diagonal(sim_matrix, np.nan)  # 排除自身

        # 提取均值
        valid_bank_list = valid_banks.index.tolist()
        for i, bank in enumerate(valid_bank_list):
            cogn_results[(bank, year)] = float(np.nanmean(sim_matrix[i]))

        # 无效银行 → NaN
        for bank in bank_list:
            if (bank, year) not in cogn_results:
                cogn_results[(bank, year)] = np.nan

        n_valid = len(valid_banks)
        year_vals = [v for k, v in cogn_results.items()
                     if k[1] == year and not np.isnan(v)]
        mean_val = np.mean(year_vals) if year_vals else float('nan')
        logger.info(f"  年份 {year}: {n_valid}/{n_banks} 有效银行, "
                    f"cogn_mean 均值={mean_val:.4f}")

    # 合并至面板
    if cogn_results:
        cogn_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1], 'bank_cogn_mean': v}
            for k, v in cogn_results.items()
        ])
        panel = panel.merge(cogn_df, on=['target_bank', 'year'], how='left')

        # 范围断言: TF-IDF 向量非负 → cosine ∈ [0, 1]
        valid_vals = panel['bank_cogn_mean'].dropna()
        if len(valid_vals) > 0:
            assert (valid_vals >= -1e-10).all() and (valid_vals <= 1 + 1e-10).all(), \
                f"bank_cogn_mean 超出 [0,1]: [{valid_vals.min():.6f}, {valid_vals.max():.6f}]"
            n_valid_total = valid_vals.notna().sum()
            logger.info(f"  认知邻近度已合并: {n_valid_total:,} 有效值, "
                        f"mean={valid_vals.mean():.4f}, std={valid_vals.std():.4f}")
    else:
        logger.warning("  未生成任何认知邻近度变量")

    return panel


# ============================================================================
# 7. Embedding 同业网络控制变量
# ============================================================================
# 学术依据:
#   Hoberg, G., & Phillips, G. (2016). Text-based network industries and
#   endogenous product differentiation. Journal of Political Economy, 124(5),
#   1423-1465. DOI: 10.1086/688176
#   → 用产品描述文本构建动态同行网络; 本模块用 Embedding 向量相似度
#     替代 TF-IDF cosine, 捕获更深层的语义邻近度
#
#   Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings
#   using Siamese BERT-networks. EMNLP-IJCNLP 2019, 3982-3992.
#   DOI: 10.18653/v1/D19-1410
#   → Sentence-BERT 为本地降级方案提供学术依据
#
#   Manski, C. F. (1993). Identification of endogenous social effects:
#   The reflection problem. The Review of Economic Studies, 60(3), 531-542.
#   DOI: 10.2307/2298123
#   → 使用 Lag(Y-1) 规避同期反射问题
#
# 流程:
#   1. 按银行×年份聚合文本 (标题+内容)
#   2. 截断至 8000 字符 (API token 限制)
#   3. 调用 yunwu.ai/v1/embeddings (降级: sentence-transformers)
#   4. cosine_similarity → 对角线置零 → row_stochastic_normalize
#   5. emb_peer_tone = W_emb(t-1) × tone(t-1) (滞后一期)
#
# 输出:
#   emb_peer_tone_lag1_full: Embedding 加权同行情感 (控制变量)
#   bank_emb_sim_mean:       银行 Embedding 平均相似度 (控制变量)
# ============================================================================

# 读取 LLM 配置 (与 21_tone_llms.py 共享同一份 config.yaml 配置)
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
_EMB_MODELS = LLM_CONFIG.get('models', [])


async def _get_embeddings_api(texts, model='text-embedding-3-small'):
    """调用 OpenAI 兼容 /embeddings 端点获取文本向量。

    base_url 和 api_key 从 config.yaml 的 tone_llm_processing.models[0]
    读取, 与 21_tone_llms.py 共享同一份配置, 严禁硬编码。

    Args:
        texts: list[str], 待编码文本列表
        model: str, embedding 模型名称

    Returns:
        np.ndarray, shape=(len(texts), dim), 归一化后的嵌入向量矩阵

    Raises:
        RuntimeError: API 返回非 200 状态码
    """
    import aiohttp

    if not _EMB_MODELS:
        raise RuntimeError("config.yaml 中无可用 LLM 模型配置")

    model_cfg = _EMB_MODELS[0]  # 使用第一个模型的 API 端点
    base_url = model_cfg.get('base_url', '')
    api_key = model_cfg.get('api_key', '')

    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {api_key}"}
    BATCH = 100  # OpenAI embeddings API 单次最多 2048 个输入
    all_emb = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(texts), BATCH):
            batch_texts = texts[i:i + BATCH]
            payload = {"model": model, "input": batch_texts}
            async with session.post(f"{base_url}/embeddings",
                                     json=payload, headers=headers,
                                     timeout=aiohttp.ClientTimeout(total=120)
                                     ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(
                        f"Embedding API HTTP {resp.status}: {body[:200]}")
                data = await resp.json()
                for item in sorted(data['data'], key=lambda x: x['index']):
                    all_emb.append(item['embedding'])
            logger.info(f"    Embedding batch {i // BATCH + 1}/"
                        f"{(len(texts) - 1) // BATCH + 1} 完成")
    return np.array(all_emb)


def compute_embedding_peer_network(df_exploded: pd.DataFrame,
                                    panel: pd.DataFrame) -> pd.DataFrame:
    """基于 Embedding 向量相似度的同业网络控制变量。

    使用 Sentence Embedding 将每家银行每年的新闻文本编码为向量,
    通过余弦相似度构建动态同业网络权重矩阵, 计算加权同行情感
    作为内生性处理的控制变量。

    方法论:
      - 权重矩阵 W_emb 基于 Embedding 余弦相似度, 非二值共现
      - 滞后一期 (t-1) 避免 Manski (1993) 反射问题
      - API 优先, sentence-transformers 降级保护

    Args:
        df_exploded: 文章级 DataFrame, 含 target_bank/year/标题/内容
        panel: 银行-年份面板 DataFrame

    Returns:
        panel: 追加 emb_peer_tone_lag1_full, bank_emb_sim_mean 列的面板

    References:
        Hoberg, G., & Phillips, G. (2016). JPE, 124(5), 1423-1465.
        Reimers, N., & Gurevych, I. (2019). EMNLP-IJCNLP 2019.
        Manski, C. F. (1993). RES, 60(3), 531-542.
    """
    import asyncio

    logger.info("=" * 60)
    logger.info("Embedding 同业网络控制变量 (Hoberg & Phillips 2016)")
    logger.info("=" * 60)

    text_col = '内容'
    title_col = '标题'
    tone_col = 'llm_vote_tone_full'
    MAX_CHARS = 8000  # 截断阈值: ~4000 中文字 ≈ 5000 tokens

    if tone_col not in panel.columns:
        logger.warning(f"  {tone_col} 不存在, 跳过 Embedding 同业网络")
        return panel

    years = sorted(panel['year'].unique())
    emb_results = {}  # key: (bank, year), value: dict

    for year in years:
        lag_year = year - 1
        df_lag = df_exploded[df_exploded['year'] == lag_year]

        if df_lag.empty:
            logger.info(f"  年份 {year}: 滞后年 {lag_year} 无数据, 跳过")
            continue

        # ── 1. 按银行聚合文本 (复用 _concat_text 模式) ──
        def _concat_text_emb(group):
            bodies = group[text_col].fillna('').astype(str)
            if title_col in group.columns:
                titles = group[title_col].fillna('').astype(str)
                return ' '.join(titles + ' ' + bodies)
            return ' '.join(bodies)

        bank_texts = df_lag.groupby('target_bank').apply(
            _concat_text_emb, include_groups=False)
        bank_list = bank_texts.index.tolist()
        n_banks = len(bank_list)

        if n_banks < 2:
            logger.info(f"  年份 {year}: 仅 {n_banks} 家银行, 跳过")
            continue

        # ── 2. 截断至 MAX_CHARS ──
        texts = [t[:MAX_CHARS] for t in bank_texts.values]

        # ── 3. 获取 Embedding (API 优先, 降级 sentence-transformers) ──
        try:
            emb_matrix = asyncio.run(_get_embeddings_api(texts))
            logger.info(f"  年份 {year}: API Embedding 成功, "
                        f"{n_banks} 银行, dim={emb_matrix.shape[1]}")
        except Exception as e:
            logger.warning(f"  年份 {year}: API embedding 失败 ({e}), "
                           f"回退 sentence-transformers")
            try:
                from sentence_transformers import SentenceTransformer
                st_model = SentenceTransformer('shibing624/text2vec-base-chinese')
                emb_matrix = st_model.encode(texts, show_progress_bar=True)
                logger.info(f"  年份 {year}: sentence-transformers 成功, "
                            f"dim={emb_matrix.shape[1]}")
            except Exception as e2:
                logger.error(f"  年份 {year}: Embedding 完全失败 ({e2}), 跳过")
                continue

        # ── 4. cosine_similarity → 对角线置零 → 行随机标准化 ──
        if HAS_SKLEARN:
            sim_matrix = _cosine_sim(emb_matrix)
        else:
            # 手动计算: 归一化后点积
            norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            normed = emb_matrix / norms
            sim_matrix = normed @ normed.T

        np.fill_diagonal(sim_matrix, 0)  # 自身不算同行
        sim_df = pd.DataFrame(sim_matrix, index=bank_list, columns=bank_list)
        W_emb = row_stochastic_normalize(sim_df)

        # ── 5. emb_peer_tone = W_emb(t-1) × tone(t-1) ──
        panel_lag = panel[panel['year'] == lag_year].set_index('target_bank')
        tone_vec = pd.Series(np.nan, index=bank_list)
        for bank in bank_list:
            if bank in panel_lag.index:
                val = panel_lag.loc[bank, tone_col]
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                tone_vec[bank] = val

        emb_peer_tone = W_emb.values @ tone_vec.fillna(0).values

        for idx, bank in enumerate(bank_list):
            # 平均相似度: 该银行与所有其他银行的 Embedding 余弦相似度均值
            sim_row = sim_matrix[idx].copy()
            sim_mean = float(np.mean(sim_row[sim_row > 0])) if (sim_row > 0).any() else np.nan

            emb_results[(bank, year)] = {
                'emb_peer_tone_lag1_full': emb_peer_tone[idx],
                'bank_emb_sim_mean': sim_mean,
            }

        logger.info(f"  年份 {year}: {n_banks} 家银行, "
                    f"Embedding 同行情感均值={np.nanmean(emb_peer_tone):.4f}")

    # 合并至面板
    if emb_results:
        emb_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1], **v}
            for k, v in emb_results.items()
        ])
        panel = panel.merge(emb_df, on=['target_bank', 'year'], how='left')

        # 范围断言
        valid_sim = panel['bank_emb_sim_mean'].dropna()
        if len(valid_sim) > 0:
            assert (valid_sim >= -1e-10).all() and (valid_sim <= 1 + 1e-10).all(), \
                f"bank_emb_sim_mean 超出 [0,1]: [{valid_sim.min():.6f}, {valid_sim.max():.6f}]"
            logger.info(f"  Embedding 同业网络已合并: {len(valid_sim):,} 有效值, "
                        f"sim_mean={valid_sim.mean():.4f}")
    else:
        logger.warning("  未生成任何 Embedding 同业网络变量")

    return panel
