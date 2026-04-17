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

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

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
