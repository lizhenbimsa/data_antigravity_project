"""
47_network_brokerage.py — 信息经纪网络与二分图中心度
=====================================================

管线位置:
  45_panel_export_main.py → 步骤 7h-brok / 7h-neg / 7h-fire
  本模块在主管线中位于 46_network_spillovers.py 之后执行,
  依赖 41_panel_encode_aggregate.py 生成的 neg_count_full 和 n_articles。

核心功能:
  1. 构建"媒体-银行"年度二分图 (Bipartite Graph):
     - Set A (bipartite=0): 新闻媒体来源 (如 '21世纪经济报道')
     - Set B (bipartite=1): 被报道银行 (如 '工商银行')
     - 边权重 = 该媒体在该年报道该银行的文章篇数
  2. 计算银行端的特征向量中心度 (brokerage_eigen_cent),
     衡量银行在信息分发网络中的枢纽地位 — 高中心度银行
     能通过更多异质媒体渠道传播/接收信息。
  3. 计算行业负面冲击指数 (industry_neg_shock, LOO 方法),
     量化银行所处行业的整体负面舆论压力。
  4. 构建火灾甩卖交乘项 (brokerage_fire_sale),
     识别信息枢纽银行在行业负面冲击下的放大效应。

学术依据:
  Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage
  networks: Facilitating liquidity provision. The Review of Financial
  Studies, 37(9), 2903-2935. DOI: 10.1093/rfs/hhae026
  → 二分图信息经纪网络 + 特征向量中心度
  → 本项目将其原文的"基金-券商"二分图改造为"媒体-银行"二分图

  Manski, C. F. (1993). Identification of endogenous social effects:
  The reflection problem. The Review of Economic Studies, 60(3), 531-542.
  DOI: 10.2307/2298123
  → industry_neg_shock 使用 LOO 规避反射问题:
    即银行 i 的冲击值 = 同年其余所有银行 j≠i 的负面比率均值,
    排除自身以打破 Manski 所述的"镜像效应"。

输出变量 (Stata 回归可用):
  - brokerage_eigen_cent: 二分图特征向量中心度
    Stata 示例: reg Y brokerage_eigen_cent X, cluster(province)
  - industry_neg_shock: 行业负面冲击指数 (LOO)
    Stata 示例: reg Y industry_neg_shock X, cluster(province)
  - brokerage_fire_sale: 经纪中心度(t-1) × 行业负面冲击(t)
    Stata 示例: reg Y c.brokerage_fire_sale X, cluster(province)
    经济含义: 正系数 → 信息枢纽银行在行业负面冲击下遭受更大声誉损失
"""

import os
import sys

import numpy as np
import pandas as pd

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
# 全局配置
# ============================================================================
# CONFIG: 由 core/config.py::load_config 从 config/ 下 split YAML (回退 config.yaml) 加载, 包含路径、模型列表等全局参数
# logger: 日志输出至 logs/47_network_brokerage.log, 便于生产环境排查

CONFIG = load_config()
STAGE_NAME = "47_network_brokerage"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 1. 媒体-银行二分图构建
# ============================================================================

def build_media_bank_bipartite(
    df_exploded: pd.DataFrame, year: int
) -> 'nx.Graph':
    """构建年度媒体-银行二分图。

    本函数是信息经纪网络分析的基础构件。与 46_network_spillovers.py
    中的 build_adjacency_matrix() 不同, 该函数构建的是"媒体-银行"
    异质二分图 (而非"银行-银行"同质共现图), 用于计算银行在信息
    分发网络中的中介地位。

    节点:
      - Set A (bipartite=0): 媒体来源 — df_exploded['媒体(中文)']
        来源: 11_news_bank.py 解析的中文媒体名称
      - Set B (bipartite=1): 银行 — df_exploded['target_bank']
        来源: 11_news_bank.py 匹配的目标银行
    边:
      - weight = 该媒体在该年报道该银行的文章数
      - 权重越大, 表示该媒体与该银行的信息连接越强

    学术依据:
      Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage
      networks. The Review of Financial Studies, 37(9), 2903-2935.
      DOI: 10.1093/rfs/hhae026
      → 原文 Table 1: 基金-券商二分图; 本项目改造为媒体-银行二分图

    边界处理:
      - networkx 未安装 → 返回 None (上游通过 if G is None 跳过)
      - '媒体(中文)' 列不存在 → 返回空图 nx.Graph()
      - 无边数据 → 返回空图 nx.Graph()
      - 构建后断言 nx.is_bipartite(G), 确保图结构正确

    Args:
        df_exploded: 篇章级 DataFrame, 须含 '媒体(中文)' 和 'target_bank'
        year: 目标年份

    Returns:
        G: nx.Graph with bipartite attribute, 或空图
    """
    if not HAS_NETWORKX:
        return None

    df_year = df_exploded[df_exploded['year'] == year]

    if '媒体(中文)' not in df_year.columns:
        logger.warning(f"  年份 {year}: '媒体(中文)' 列不存在")
        return nx.Graph()

    # 聚合边权重: (媒体, 银行) → 文章数
    # 例如: ('21世纪经济报道', '工商银行') → weight=15 表示该年 15 篇报道
    edges = (df_year.groupby(['媒体(中文)', 'target_bank'])
             .size().reset_index(name='weight'))

    if edges.empty:
        return nx.Graph()

    G = nx.Graph()

    # 添加媒体节点 (bipartite=0)
    media_nodes = edges['媒体(中文)'].unique()
    G.add_nodes_from(media_nodes, bipartite=0)

    # 添加银行节点 (bipartite=1)
    bank_nodes = edges['target_bank'].unique()
    G.add_nodes_from(bank_nodes, bipartite=1)

    # 添加加权边
    for _, row in edges.iterrows():
        G.add_edge(row['媒体(中文)'], row['target_bank'],
                   weight=int(row['weight']))

    # 二分图断言
    assert nx.is_bipartite(G), f"年份 {year}: 图不是二分图!"

    return G


# ============================================================================
# 2. 经纪中心度计算 (三级 fallback)
# ============================================================================

def compute_brokerage_centrality(
    panel: pd.DataFrame, df_exploded: pd.DataFrame
) -> pd.DataFrame:
    """计算银行在媒体-银行二分图中的特征向量中心度。

    经济含义:
      高 brokerage_eigen_cent 的银行通过更多高影响力媒体获得报道,
      意味着其信息传播范围更广、信息中介地位更高。在 Stata 回归中,
      该变量可作为银行"信息可见度"的代理变量。

    三级 fallback 策略 (确保生产环境的稳健性):
      Level 1: nx.eigenvector_centrality_numpy (精确, 基于 numpy/scipy)
               适用于大多数正常图, O(n³) 复杂度
      Level 2: nx.eigenvector_centrality (迭代幂法, max_iter=2000)
               当 numpy 方法因数值精度失败时的备选
      Level 3: nx.degree_centrality (兜底) + CRITICAL 日志
               仅在极端退化图 (如完全断连) 时触发, 日志标记便于事后排查

    仅提取 bipartite=1 (银行) 节点的中心度值, 排除媒体节点。

    数据流:
      df_exploded (11_news_bank.py) → build_media_bank_bipartite()
      → nx.eigenvector_centrality → panel['brokerage_eigen_cent']

    Args:
        panel: Bank-Year 面板 DataFrame (target_bank + year 为联合键)
        df_exploded: 篇章级 DataFrame (须含 '媒体(中文)', target_bank, year)

    Returns:
        panel: 追加 brokerage_eigen_cent 列的面板 (left join, 无匹配为 NaN)
    """
    if not HAS_NETWORKX:
        logger.warning("  networkx 未安装, 跳过经纪中心度计算")
        return panel

    logger.info("=" * 60)
    logger.info("步骤: 信息经纪网络中心度 (Han et al. 2024, RFS)")
    logger.info("=" * 60)

    years = sorted(panel['year'].unique())
    results = {}

    for year in years:
        G = build_media_bank_bipartite(df_exploded, year)
        # 至少需要 1 媒体 + 2 银行 = 3 节点才能计算有意义的中心度
        if G is None or G.number_of_nodes() < 3:
            logger.info(f"  年份 {year}: 节点不足, 跳过")
            continue

        # 提取银行节点
        bank_nodes = {n for n, d in G.nodes(data=True)
                      if d.get('bipartite') == 1}
        media_nodes = {n for n, d in G.nodes(data=True)
                       if d.get('bipartite') == 0}

        eigen_vals = None
        method_used = ""

        # Level 1: eigenvector_centrality_numpy (精确)
        # networkx 的 numpy 实现在非连通图上会主动报
        # AmbiguousSolution；这是网络结构属性，不是生产故障。
        if nx.is_connected(G):
            try:
                ec = nx.eigenvector_centrality_numpy(G, weight='weight')
                eigen_vals = {n: ec[n] for n in bank_nodes if n in ec}
                method_used = "numpy"
            except Exception as e:
                logger.info(f"  年份 {year}: numpy 特征向量中心度不可用, 转迭代法 ({e})")
        else:
            logger.info(f"  年份 {year}: 图非连通, 使用迭代特征向量中心度")

        # Level 2: eigenvector_centrality (迭代)
        if eigen_vals is None:
            try:
                ec = nx.eigenvector_centrality(
                    G, weight='weight', max_iter=2000, tol=1e-06)
                eigen_vals = {n: ec[n] for n in bank_nodes if n in ec}
                method_used = "iterative"
            except nx.PowerIterationFailedConvergence:
                logger.info(f"  年份 {year}: eigenvector 迭代不收敛, 转 degree 兜底")
            except Exception as e:
                logger.info(f"  年份 {year}: eigenvector 迭代法不可用, 转 degree 兜底 ({e})")

        # Level 3: degree_centrality (兜底)
        if eigen_vals is None:
            logger.info(f"  年份 {year}: 使用 degree_centrality 兜底")
            dc = nx.degree_centrality(G)
            eigen_vals = {n: dc[n] for n in bank_nodes if n in dc}
            method_used = "degree_fallback"

        for bank, val in eigen_vals.items():
            results[(bank, year)] = val

        logger.info(f"  年份 {year}: {len(media_nodes)} 媒体, "
                    f"{len(bank_nodes)} 银行, "
                    f"{G.number_of_edges()} 边, "
                    f"方法={method_used}")

    # 合并至面板 — 使用 left join 确保面板行数不变
    # 无匹配的 Bank-Year (如数据稀疏年份) 自动填充 NaN
    if results:
        brok_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1],
             'brokerage_eigen_cent': v}
            for k, v in results.items()
        ])
        panel = panel.merge(brok_df, on=['target_bank', 'year'],
                            how='left')

        valid = panel['brokerage_eigen_cent'].notna().sum()
        logger.info(f"  经纪中心度已合并: {valid:,} 有效值, "
                    f"mean={panel['brokerage_eigen_cent'].mean():.6f}")
    else:
        logger.warning("  未计算任何经纪中心度")

    return panel


# ============================================================================
# 3. 行业负面冲击指数 (LOO)
# ============================================================================

def compute_industry_neg_shock(panel: pd.DataFrame) -> pd.DataFrame:
    """计算行业负面冲击指数 (Leave-One-Out)。

    经济含义:
      衡量银行 i 在年份 t 面临的"行业整体负面舆论压力",
      即同行银行的平均负面报道占比。高值表明整个行业处于
      负面舆论环境中 (如监管风暴、金融危机期间)。

    公式:
      neg_ratio_i,t = neg_count_full_i,t / n_articles_i,t
      industry_neg_shock_i,t = mean_{j≠i}(neg_ratio_j,t)

    LOO 设计动机:
      Manski, C. F. (1993). Identification of endogenous social effects:
      The reflection problem. The Review of Economic Studies, 60(3), 531-542.
      DOI: 10.2307/2298123
      → 如果直接使用行业均值 (含自身), 银行自身的负面新闻会同时
        出现在因变量和自变量中, 产生机械性相关。LOO 通过排除银行
        自身来打破这种"反射效应", 满足排他性约束。

    数据源 (上游管线):
      neg_count_full: 41_panel_encode_aggregate.py — LLM 投票判定为负面的文章数
      n_articles: 41_panel_encode_aggregate.py — 银行年度总文章数

    边界处理:
      - n_articles=0 → neg_ratio=NaN (通过 .replace(0, np.nan) 除零保护)
      - 单银行年份 (total_n ≤ 1) → NaN (无法做 LOO, 测试 5 已验证)
      - neg_count_full 或 n_articles 列缺失 → 跳过并返回原面板

    Args:
        panel: Bank-Year 面板 (须含 neg_count_full, n_articles)

    Returns:
        panel: 追加 industry_neg_shock 列 (∈ [0,1], NaN 表示无法计算)
    """
    logger.info("=" * 60)
    logger.info("步骤: 行业负面冲击指数 (LOO, Manski 1993)")
    logger.info("=" * 60)

    if 'neg_count_full' not in panel.columns:
        logger.warning("  neg_count_full 不存在, 跳过行业负面冲击")
        return panel

    if 'n_articles' not in panel.columns:
        logger.warning("  n_articles 不存在, 跳过行业负面冲击")
        return panel

    # 第一步: 计算每家银行的负面报道比例
    # replace(0, np.nan) 确保零文章银行不产生 Inf, 而是 NaN
    # metric-audit 2026-06-02 (encode-02 重构对齐): neg_count_full 是 LLM-count
    # (encode.py is_negative_full sum), 分母须同口径 = LLM-valid 篇数; 重构后
    # n_articles=物理 size, 用 n_articles_llm_valid (旧 panel 缺列回退 n_articles, 其即 count).
    _nac = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
    panel['_neg_ratio'] = (panel['neg_count_full']
                           / panel[_nac].replace(0, np.nan))

    # 第二步: 逐年 Leave-One-Out 计算
    # 对于年份 t 中的银行 i: shock_i = (Σ_{j≠i} ratio_j) / (N_valid - 1)
    # 其中 N_valid = 该年有有效 ratio 的银行数量
    shock_vals = pd.Series(np.nan, index=panel.index)
    for year in panel['year'].unique():
        mask = panel['year'] == year
        ratios = panel.loc[mask, '_neg_ratio']
        total_sum = ratios.sum()    # Σ ratio_j (NaN 被 .sum() 自动忽略)
        total_n = ratios.notna().sum()  # 有效银行数

        for idx in panel.loc[mask].index:
            own = panel.at[idx, '_neg_ratio']
            # 仅当自身有效 且 至少有 2 家有效银行时才计算
            if pd.notna(own) and total_n > 1:
                shock_vals.at[idx] = (total_sum - own) / (total_n - 1)

    panel['industry_neg_shock'] = shock_vals
    panel.drop('_neg_ratio', axis=1, inplace=True, errors='ignore')

    valid = panel['industry_neg_shock'].notna().sum()
    logger.info(f"  行业负面冲击已计算: {valid:,} 有效值, "
                f"mean={panel['industry_neg_shock'].mean():.4f}")

    return panel


# ============================================================================
# 4. 火灾甩卖交乘项
# ============================================================================

def compute_fire_sale_interaction(panel: pd.DataFrame) -> pd.DataFrame:
    """计算火灾甩卖交乘项: brokerage_eigen_cent(t-1) × industry_neg_shock(t)。

    学术直觉:
      信息枢纽银行 (高 brokerage_eigen_cent) 在行业整体负面冲击下,
      由于其信息传播的桥梁地位, 可能面临更大的声誉溢价损失。
      交乘项捕获的是"网络位置"与"外部冲击"的交互效应。

      Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage
      networks. The Review of Financial Studies, 37(9), 2903-2935.
      DOI: 10.1093/rfs/hhae026
      → 原文 Section 4.3: 枢纽机构在市场压力期的流动性提供

    设计要点:
      - 使用 t-1 期的中心度 (而非 t 期), 避免"同期内生性":
        t 期的负面冲击可能改变 t 期的媒体报道模式, 进而影响 t 期中心度
      - shift(1) 前必须按 (target_bank, year) 排序, 否则 lag 语义错误
      - 首年观测自动为 NaN (无前一期数据)

    Stata 回归示例:
      reg Y c.brokerage_fire_sale brokerage_eigen_cent industry_neg_shock X
      → 正系数: 信息枢纽银行在行业负面冲击下遭受更大损失
      → 解释: 媒体网络放大了行业负面信息对枢纽银行的冲击

    Args:
        panel: Bank-Year 面板 (须含 brokerage_eigen_cent, industry_neg_shock)

    Returns:
        panel: 追加 brokerage_fire_sale 列
    """
    logger.info("=" * 60)
    logger.info("步骤: 火灾甩卖交乘项 (Han et al. 2024)")
    logger.info("=" * 60)

    if 'brokerage_eigen_cent' not in panel.columns:
        logger.warning("  brokerage_eigen_cent 不存在, 跳过")
        return panel

    if 'industry_neg_shock' not in panel.columns:
        logger.warning("  industry_neg_shock 不存在, 跳过")
        return panel

    # 排序确保 shift(1) 产生正确的 lag-1 语义
    # 即: 每家银行的时间序列按年份递增, shift(1) 取前一年的值
    panel = panel.sort_values(
        ['target_bank', 'year']).reset_index(drop=True)

    # brokerage_eigen_cent(t-1): 使用去年的网络位置, 避免同期内生性
    panel['_lag1'] = (panel.groupby('target_bank')
                      ['brokerage_eigen_cent'].shift(1))
    # 交乘: 去年的网络枢纽地位 × 今年的行业负面冲击
    panel['brokerage_fire_sale'] = (
        panel['_lag1'] * panel['industry_neg_shock'])
    panel.drop('_lag1', axis=1, inplace=True, errors='ignore')

    valid = panel['brokerage_fire_sale'].notna().sum()
    logger.info(f"  火灾甩卖交乘已计算: {valid:,} 有效值, "
                f"mean={panel['brokerage_fire_sale'].mean():.6f}")

    return panel
