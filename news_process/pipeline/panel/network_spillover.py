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
  - 邻接矩阵: A[i,j] = bank_i 与 bank_j 在 Year t 的新闻共现篇数
    (both-verified 口径: 每篇文章对每条边只计 1 次, 且仅当两家银行的
    twin 行均通过 verification 过滤幸存; fix omni-g-net-spill-01)
  - 行随机标准化: W[i,j] = A[i,j] / Σ_k A[i,k], 每行和为 1
    防止大银行规模主导网络权重 (类比空间计量的空间权重矩阵)
  - 网络压力: peer_tone_i,t = Σ_j W[i,t-1] × tone_j,t-1
  - 严格 Lag(Y-1): 用去年的网络权重 × 去年的同行情感
    避免 Manski 反射问题和同期反向因果

输入: 41_panel_encode_aggregate 生成的面板 + 篇章级 df_exploded
输出: 面板中追加 peer_tone_lag1_*、22 种中心度、bank_cogn_mean 列

T=2 样本披露 (metric-audit V3 data-02): fix(network-03) 后, 孤立银行(无共现同行)
的 peer_tone/peer_tone_2nd/peer_cov 正确置 NaN(而非伪零)。当前 T=2(2017-2018)
corpus 下, 去伪零后一阶 peer 网仅约 32 bank-year 有值、且全部落 2018 单截面;
brokerage 2SLS 有效 N≈22(含 DV), 在 absorb(bank_id year) 下 bank FE 饱和、
**不足以识别**。须待 production run 扩 T≥3 + 结局变量(ROA 等)取数后重估; 论文勿在
当前样本上声称因果。
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix

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
from news_process.pipeline.text import embedding_engine as _eng

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "46_network_spillovers"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# fix(network-metrics-audit 2026-06-13, P1-1): 共现网 bank_eigen_cent 按连通分量计算时
# 的微小分量门槛 (孤立点 / 单边对 → 特征向量平凡, 置 NaN); 与
# network_brokerage._MIN_COMPONENT_SIZE 语义一致 (3 = 最小三角)。
_CMNT_MIN_COMPONENT_SIZE = 3


# ============================================================================
# 2. 邻接矩阵构建
# ============================================================================
# fix(omni-g-net-spill-01, 2026-06-11): 主路径改按 docid 聚合 (both-verified,
# 每篇文章每对 +1), 不再消费 stage-11 的陈旧 co_mentioned_banks token —
# 该列在 stage 21 verification 过滤后仍列出已被拒绝的银行 (phantom 边来源)。
# co_mentioned_banks 仅作无 docid 旧 schema 的降级兜底。
# 该矩阵是后续所有网络指标 (溢出、中心度) 的共同基础。

def build_adjacency_matrix(
    df_exploded: pd.DataFrame,
    year: int,
    *,
    hyperedge_normalize: bool = False,
) -> tuple[pd.DataFrame, list[str]]:
    """构建年度银行共现邻接矩阵 (both-verified, 每篇文章每对 +1)。

    fix(omni-g-net-spill-01, 2026-06-11) 边权口径统一: 旧实现对 verification
    过滤后的展开帧 (article × bank) 逐行解析 stage-11 的 co_mentioned_banks
    并双向 +1 — 同一文章两 twin 行均幸存 → 该对计 2, 仅一行幸存 → 计 1
    (1x/2x 任意混合); 且 co_mentioned_banks 仍列出 verification 已拒绝的
    银行 → phantom 边入网。现按 docid 聚合: 文章 k 在帧中幸存的
    target_bank 集合 (即均通过 verification 的银行) 内每无序对 {A,B}
    恰好 A[A,B] += 1, A[B,A] += 1 (对称, 每篇文章 +1)。

    注: 由此矩阵计算的 bank_degree_cent 是 Freeman (1979) 度中心度,
    衡量银行在金融科技信息网络中的连接程度。
    (引文勘误 network-metrics-audit 2026-06-13, P2-16: 旧注称"等价于 Dahlke et al.
    2024 RP 的 degree_ai"过强 — Dahlke 的 degree_ai 是企业**超链接**网络度中心度,
    图基底与新闻共现图不同, 仅思想同源、非等价; 删除等价声称。)

    Args:
        df_exploded: 篇章级 DataFrame, 须含 docid 列 (both-verified 主路径);
            缺 docid 时按 co_mentioned_banks 旧口径降级 (见下方警告)
        year: 目标年份

    Returns:
        adj_df: 对称邻接矩阵 DataFrame (index=columns=银行列表)
        bank_list: 银行名称列表
    """
    df_year = df_exploded[df_exploded['year'] == year]

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

    if 'docid' in df_year.columns:
        # fix(omni-g-net-spill-01, 2026-06-11): both-verified 主路径 —
        # 同 docid 下幸存的 target_bank 行集合内逐无序对 +1 (每篇文章每对恰 1 次)。
        # ── 超边规模诊断 + Newman 归一选项 (network-metrics-audit 2026-06-13, P1-4) ──
        # 一篇提及 N 家银行的文章 (榜单/批量监管通报) 贡献 C(N,2) 条**等权**边, 大-N 文章
        # 可凭边数膨胀主导网络 (污染 W/W²/全部中心度)。默认仍 +1 (golden-safe);
        # hyperedge_normalize=True 时改 Newman (2001 PRE) degree-preserving 归一 —
        # 每对贡献 1/(N-1) 使单篇总度贡献守恒。
        # ⚠ 接线状态披露 (network-metrics-reaudit 2026-06-13, NB-01): hyperedge_normalize 目前是
        # **预留参数, 尚未接线**到 config/runner — 两个生产调用方 (compute_network_spillovers /
        # compute_bank_network_centrality) 及其外层签名与 runner 均不透传该参数, 故 True 分支在
        # 生产流水线中不可达。要真正产出"加权 vs 未加权 IV"稳健性对照, 须接 config 键 +
        # runner 透传 + 第二套 *_hn 列 (改值, 需重生 golden)。当前仅供直接调用 / 单测使用;
        # 默认 False 路径 (现行 +1) 不受影响。Newman 语义由 test_omni_fix_net_spill 锁定。
        _grp_sizes = df_year.groupby('docid')['target_bank'].nunique()
        _n_big = int((_grp_sizes > 10).sum())
        if _n_big:
            logger.info(
                f"  年份 {year}: {_n_big} 篇大-N 文章 (>10 家银行, "
                f"max={int(_grp_sizes.max())}) — 等权 clique 投影下可能主导网络 "
                f"(P1-4; hyperedge_normalize={hyperedge_normalize})")
        for _docid, banks in df_year.groupby('docid')['target_bank']:
            uniq = sorted(set(banks))
            _w = (1.0 / (len(uniq) - 1)) if (hyperedge_normalize and len(uniq) > 1) else 1.0
            for a_pos in range(len(uniq)):
                i = bank_to_idx[uniq[a_pos]]
                for b_pos in range(a_pos + 1, len(uniq)):
                    j = bank_to_idx[uniq[b_pos]]
                    adj[i, j] += _w
                    adj[j, i] += _w  # 对称
    else:
        # ⚠ 口径降级 (兼容兜底, 仅旧 schema/合成帧): 无 docid 键无法按文章聚合 →
        # 退回 co_mentioned_banks 逐行双向计数 (含 1x/2x 混合与 phantom 边)。
        logger.warning(
            f"  年份 {year}: df_exploded 缺 docid 列, 邻接矩阵退化为 "
            f"co_mentioned_banks 逐行计数口径 (含 1x/2x 混合与 phantom 边)")
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

    白话: 给每家银行算一个"它的圈子去年舆论怎么样"的变量。哪些银行算
    同一个圈子? 看新闻里谁经常和谁被一起提到 (共现)。权重做了行标准化
    (每行加起来等于 1), 这样大银行不会光靠新闻多就主导别人的圈子值。
    刻意全部用**去年**的数据 (网络也用去年的、情感也用去年的), 避免
    "我影响圈子、圈子又同时影响我"的同期互相纠缠 (Manski 反射问题)。

    Args:
        panel: Bank-Year 面板 DataFrame
        df_exploded: 篇章级 DataFrame

    Returns:
        panel: 追加 peer_tone_lag1_* 列的面板
    """
    logger.info("=" * 60)
    logger.info("步骤: 同行网络传染/溢出效应计算")
    logger.info("=" * 60)

    # fix(omni-g-net-spill-01, 2026-06-11): docid 是 both-verified 主路径键;
    # co_mentioned_banks 仅作降级兜底 — 两者皆缺才跳过。
    if ('docid' not in df_exploded.columns
            and 'co_mentioned_banks' not in df_exploded.columns):
        logger.warning("  docid / co_mentioned_banks 列均不存在, 跳过网络溢出计算")
        return panel

    # 确保年份列
    if 'year' not in df_exploded.columns:
        logger.warning("  year 列不存在, 跳过网络溢出计算")
        return panel

    years = sorted(panel['year'].unique())
    logger.info(f"  面板年份范围: {min(years)}-{max(years)}, 共 {len(years)} 年")

    # 情感列: 使用 llm_vote_tone_full 作为核心情感指标
    # 三轨 (full/ctx/ss): ss = 银行+金科同句共现轨 (content_ss; 回退=镜像 ctx→全文 body)。
    # 同行网络 W 由共现邻接矩阵决定 (track-agnostic), 故 ss 轨复用同一 W 传播 llm_vote_tone_ss,
    # 零额外计算 ($0); 缺 llm_vote_tone_ss 列时该轨经下方 `if col in panel.columns` 守卫优雅跳过。
    tone_cols = []
    for track in ['_full', '_ctx', '_ss']:
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

            # 网络加权同行均值 (row-stochastic spatial lag, LeSage-Pace 2009; Leary-Roberts 2014)。
            # fix(netspill-peertone-fillna, metric-audit 2026-06-10): 原实现 tone_vec.fillna(0)
            # 把"在网但滞后 tone 缺失"的同行以 0 注入分子, 而其权重仍留在行和(=1)分母 →
            # 加权均值系统性向 0 衰减(伪零/attenuation)。正确做法: 仅对 OBSERVED-tone 同行
            # 求加权均值, 并按观测同行的权重和重新归一化; 无观测同行 → NaN (并入 network-03
            # 孤立银行守卫: denom>0 同时覆盖"有同行"与"有观测-tone 同行")。
            W_arr = W.values
            tone_arr = tone_vec.to_numpy(dtype=float)
            obs_mask = ~np.isnan(tone_arr)
            tone_obs = np.where(obs_mask, tone_arr, 0.0)  # 未观测置 0, 其权重亦从分母剔除
            denom1 = W_arr[:, obs_mask].sum(axis=1)
            with np.errstate(invalid='ignore', divide='ignore'):
                peer_tone = (W_arr @ tone_obs) / denom1
            peer_tone = np.where(denom1 > 0, peer_tone, np.nan)

            # 二阶溢出 (邻居的邻居, LeSage & Pace 2009): W² 去对角自反馈
            # fix(network-01, Bramoullé-Djebbari-Fortin 2009 JoE): 排除 W² 对角, 否则作高阶
            # IV 含本行自身滞后 tone 违排他性。同样仅对观测同行重归一 (与一阶同口径)。
            # ⚠ 行为披露 (NSP-B): 因 W² 去对角后行和≠1, 本重归一对**所有行**(非仅缺 tone 行)
            # 改变 peer_tone_2nd 标度 —— 从旧"路径概率加权和"变为"二阶邻居加权均值"(更可解释,
            # 与一阶同口径)。peer_tone_2nd 作 brokerage IV 工具变量 (brokerage_network spec)。
            # fix(omni-g-net-spill-06, 2026-06-11) 标度声明勘误: 本重归一是对工具的
            # **逐观测 (row-specific) 确定性变换**, 不是全局标量缩放 — 2SLS 仅对工具集的
            # 全局非奇异线性变换不变, 行特定除数会改变工具的截面变异、第一阶段系数与
            # F 统计量 (旧注释"相关性不变"不成立)。
            # ⚠ 识别勘误 (network-metrics-audit 2026-06-13, P1-5): 旧注"除数由外生网络结构
            # 确定 → 外生性不受影响"在重归一估计量下**技术不准确**。除数 = 仅对 observed-tone
            # 同行 (obs_mask=~isnan(tone), 即"去年被媒体充分报道并产出 valid 票"的同行) 的权重
            # 和 → 该**求和索引集是数据可观测性/覆盖选择集, 非纯网络结构**。媒体覆盖与银行规模/
            # 事件强度系统相关 → 空间权重 W 的有效支撑内生于结果相关的选择变量 (违 SLX/peer-
            # effects 固定外生 W 前提)。须区分"行特定确定性缩放"(保外生) 与"支撑集选择性"
            # (obs_mask 内生于覆盖, 引入选择偏误)。生产 run 须提供"全在网同行/平衡覆盖子样本"
            # 稳健性对照 + 论证 W 条件下 MAR。W² 去对角守住的只是**机械**排他 (不含本行自身
            # 滞后 tone), 不涵盖此覆盖选择问题。
            W2 = W_arr @ W_arr
            np.fill_diagonal(W2, 0.0)
            denom2 = W2[:, obs_mask].sum(axis=1)
            with np.errstate(invalid='ignore', divide='ignore'):
                peer_tone_2nd = (W2 @ tone_obs) / denom2
            peer_tone_2nd = np.where(denom2 > 0, peer_tone_2nd, np.nan)

            # 存储结果（使用字典累积, 避免多 tone_col 合并丢失）
            suffix = tone_col.replace('llm_vote_tone', '')
            for idx, bank in enumerate(bank_list):
                key = (bank, year)
                if key not in peer_dict:
                    peer_dict[key] = {'target_bank': bank, 'year': year}
                peer_dict[key][f'peer_tone_lag1{suffix}'] = peer_tone[idx]
                peer_dict[key][f'peer_tone_2nd_lag1{suffix}'] = peer_tone_2nd[idx]

        # ── 同行金融科技声量溢出 ──
        # 锚点勘误 (metric-audit 2026-06-10): 原注引 Berger et al. (2022, JFI 49)
        # "Economic policy uncertainty and bank liquidity hoarding" 与本构念不符 ——
        # 该文研究宏观 EPU 指数对银行流动性囤积的影响, 并未定义同行共提网络的
        # 行随机空间滞后。本构念 (row-stochastic 同行声量溢出) 的正确锚点是:
        #   LeSage, J. & Pace, R. K. (2009). Introduction to Spatial Econometrics.
        #     → 行随机权重矩阵 W 的空间滞后 W*y 作同行加权均值。
        #   Leary, M. T. & Roberts, M. R. (2014). Do peer firms affect corporate
        #     financial policy? Journal of Finance, 69(1), 139-178. → 同行均值范式。
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
            # fix(netspill-peercov-fillna, metric-audit 2026-06-10): 与 peer_tone 同型修复 ——
            # 仅对 OBSERVED-coverage 同行求加权均值并按其权重和重归一, 而非 fillna(0) 把
            # 缺失/在网无值同行伪零注入。原 completeness-01 仅加孤立行 NaN 守卫(W 行全 0),
            # 未修"在网但 ln_coverage 缺失"的伪零(与 peer_tone 同病根)。denom>0 并入孤立守卫。
            cov_arr = cov_vec.to_numpy(dtype=float)
            cov_mask = ~np.isnan(cov_arr)
            cov_obs = np.where(cov_mask, cov_arr, 0.0)
            denom_c = W.values[:, cov_mask].sum(axis=1)
            with np.errstate(invalid='ignore', divide='ignore'):
                peer_cov = (W.values @ cov_obs) / denom_c
            peer_cov = np.where(denom_c > 0, peer_cov, np.nan)
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
      - eigenvector 三级 fallback: 全图 power → numpy(LCC) → NaN;
        非主分量/非 LCC 银行两级均兜底 0.0 (fix omni-g-net-spill-05,
        退化语义跨年一致, 不随数值收敛性漂移)
      - 断连图: CFB/eccentricity/avg_path 仅对最大连通分量计算

    白话: 中心度回答"这家银行在新闻共现网络里有多居中/多重要"。不同指标
    量的是不同的"重要": degree=认识多少邻居, betweenness=多少最短路径必须
    经过它 (桥梁地位), eigenvector/katz=邻居本身重不重要, constraint=它的
    邻居之间是否互相认识 (结构洞)。路径类指标要把"共现越多=关系越近"翻译
    成"距离越短", 所以建图时边权取倒数 (1/共现次数)。
    ⚠ 另注 (memory: panel-3-network-cols-nondeterministic): bank_clustering /
    cfbetween / harmonic 三列受 BLAS 浮点漂移影响, 跨次重建非逐位可复现。

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

        # (2) Strength Centrality — 加权度 (node strength, Opsahl-Agneessens-Skvoretz
        # 2010), 再除以**年内最大加权度** max-normalize。
        # ⚠ 口径披露 (network-metrics-audit 2026-06-13, P2-7): (a) Opsahl 2010 只定义
        #   node strength=Σw_ij, **不**按网络内最大值归一 → max-normalize 是本项目 ad-hoc
        #   实现细节、非 Opsahl 口径 (export 标签 "Opsahl 2010" 仅指 strength 构念本身);
        #   (b) 该归一是**年相对**度量 (每年最大加权度银行恒=1.0), 跨年水平不可比, 且除以
        #   年特定标量在含年 FE 回归中是乘性重标度、无法被加性年 FE 吸收 → 若升为回归 RHS
        #   须先改结构性归一 (ln(strength)/全样本归一/within-bank z)。当前仅 Table 1
        #   描述统计消费, 无 Stata 模板 RHS 引用。
        strength = dict(G.degree(weight='weight'))
        max_str = max(strength.values()) if strength else 1.0
        if max_str == 0:
            max_str = 1.0
        for b in bank_list:
            metrics[b]['bank_strength_cent'] = strength.get(b, 0.0) / max_str

        # (5) Eigenvector Centrality — 按连通分量分别计算 (分量内归一)
        # fix(network-metrics-audit 2026-06-13, P1-1): 旧实现在**整图 G** 上跑 power 迭代,
        # 断连图下不抛 PowerIterationFailedConvergence 而是收敛, 把特征向量质量全压到谱半径
        # 最大的分量 → 其余分量 (含 LCC, 若 LCC 谱半径非最大) 银行得 ~1e-42 数值残渣 (非 NaN,
        # 被回归当"中心度极低的真银行"); 且 eigen_done=True 锁死, numpy(LCC) fallback 永不触发。
        # 主控实证: 断连图非主导分量节点得 3e-42~5e-42 残渣。全量 T=18 共现网几乎必然断连 →
        # 大面积污染。同型 bug 在 network_brokerage._eigenvector_centrality_by_component 已修,
        # 此处移植同款逻辑: 每连通分量 (≥_CMNT_MIN_COMPONENT_SIZE 节点) 内单独确定性 eigenvector
        # + 分量内归一; 微小分量置 NaN (left-join 后缺失, 与 brokerage 侧 NaN 约定一致, 不再写
        # 0/残渣)。⚠ 披露: 中心度水平仅**分量内**可比 (networkx 在子图范围内 L2 归一); 跨分量
        # 比较只在"是否处于大分量"意义上成立。复用上方已算的 components (L4 步)。
        eig_vals: dict = {}
        _n_tiny_eig = 0
        for _comp in components:
            if len(_comp) < _CMNT_MIN_COMPONENT_SIZE:
                _n_tiny_eig += 1
                continue
            _sub = G.subgraph(_comp)
            try:
                _ec = nx.eigenvector_centrality(
                    _sub, weight='weight', max_iter=2000, tol=1e-06)
            except nx.PowerIterationFailedConvergence:
                # 分量内 degree 兜底 (仅极端退化分量); 与特征向量构念不同, 升 CRITICAL
                logger.critical(
                    f"  年份 {year}: {len(_comp)} 节点分量幂迭代不收敛, "
                    f"该分量 bank_eigen_cent 用 degree_centrality 兜底")
                _ec = nx.degree_centrality(_sub)
            eig_vals.update(_ec)
        for b in bank_list:
            metrics[b]['bank_eigen_cent'] = eig_vals.get(b, np.nan)
        if _n_tiny_eig:
            logger.info(f"  年份 {year}: {_n_tiny_eig} 个微小分量 "
                        f"(<{_CMNT_MIN_COMPONENT_SIZE} 节点) 的 bank_eigen_cent 置 NaN")

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

        # (11) Hub (Top ~10% by degree)
        # fix(network-metrics-audit 2026-06-13, N-08): 旧实现按 degree 降序硬切前 top10_count
        # 家 → 边界并列度银行 (第 k/k+1 名同 degree) 由 sort 字典序任意决定 hub=1/0。改阈值法:
        # 取第 top10_count 名 degree 为 cutoff, 所有 degree>=cutoff 银行均 hub=1 (并列同判,
        # 确定且不任意)。⚠ 跨年 N 变化下"~10%"绝对阈值仍漂移 → bank_is_hub 跨年不可比,
        # 宜作年内相对指示而非跨年水平变量。
        # fix(network-metrics-reaudit 2026-06-13, N-08/NB-05 退化 guard): 若 cutoff<=0
        # (全孤立年: 该年无共现对, 全部 degree=0) 或 degree 分布退化为单一值 (正则图,
        # 所有银行同 degree), 则 ">=cutoff" 会把**全部**银行收入 → bank_is_hub 沦为常数列
        # (零方差, 进回归被吸收且"人人皆枢纽"违构念)。此时置 0 (该年无明确 hub), 严格优于
        # 旧 top-k 实现在此退化下的任意 1 家。全量 T=18 稀疏早年 / 试跑样本均可命中。
        deg_sorted = sorted((metrics[b]['bank_degree_cent'] for b in bank_list),
                            reverse=True)
        top10_count = max(1, int(len(deg_sorted) * 0.10))
        _hub_cutoff = deg_sorted[top10_count - 1]
        _hub_degenerate = (_hub_cutoff <= 0) or (len(set(deg_sorted)) == 1)
        for b in bank_list:
            if _hub_degenerate:
                metrics[b]['bank_is_hub'] = 0
            else:
                metrics[b]['bank_is_hub'] = (
                    1 if metrics[b]['bank_degree_cent'] >= _hub_cutoff else 0)

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
        # ⚠ 口径披露 (network-metrics-audit 2026-06-13, N-04): 此处用**无权**度
        # (G.degree(b)=邻居数), 故 net_degree_gini_yr 衡量"连接数(degree)不平等",
        # **不是**加权共现网的"强度(strength)分布不平等"(后者需 weight='weight')。
        # 这是有意选择(拓扑连接集中度), 与 bank_strength_cent 加权口径不同, 勿混读;
        # codebook 标签宜明确为 connection-count Gini。
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

    操作化 (项目自定义 — 引文勘误 network-metrics-audit 2026-06-13, P2-16):
      cogn_mean = 每家银行与所有其他银行的 TF-IDF char-ngram cosine 均值,
      作为 Boschma (2005) 认知邻近度构念的**本项目自定义操作化**。
      ⚠ 旧注把该操作化归因于 Dahlke et al. (2024, RP) 不成立: 该文方法是用
      transformer 从企业网站文本识别 AI 采纳 + 构建企业间**超链接**网络度中心度,
      全文不含"两两 TF-IDF 余弦相似度求均值=cognitive proximity"操作化。
      TF-IDF cosine 衡量"新闻话语相似度", 是否等同"知识基础相似度"须经业务相似度
      基准外部效度验证 (Jaffe 1989 技术邻近 / Bloom-Schankerman-Van Reenen 2013
      ECMA technology closeness 为可选对照锚点)。

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
    logger.info("步骤: 认知邻近度计算 (Boschma 2005; 操作化=本项目自定义 TF-IDF cosine)")
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
            # network-metrics-audit 2026-06-13 (N-10 + rank-18): 裸 assert → 显式 raise
            # (python -O 下 assert 被剥离 → 守卫静默失效, 错误值悄悄落盘); 容差 1e-10→1e-6
            # 适配 float32 cosine 舍入 (避免边界 1.0000001 误触发)。值域语义不变, golden-safe。
            if not ((valid_vals >= -1e-6).all() and (valid_vals <= 1 + 1e-6).all()):
                raise ValueError(
                    f"bank_cogn_mean 超出 [0,1]: "
                    f"[{valid_vals.min():.6f}, {valid_vals.max():.6f}]")
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
#   1. 按银行×年份聚合文本 (标题+内容, docid 升序确定性拼接)
#   2. 超长超级文档由 embedding_engine 分块 + token 加权 mean pooling
#      (fix omni-g-net-spill-02: 旧 8000 字符前缀截断已移除 — 截断只保留
#      行序最先若干篇文章前缀, 非代表性样本)
#   3. 调用 yunwu.ai/v1/embeddings (降级: sentence-transformers)
#   4. cosine_similarity → 对角线置零 → 负值 clip → row_stochastic_normalize
#   5. emb_peer_tone = W_emb(t-1) × tone(t-1) (滞后一期)
#
# 输出:
#   emb_peer_tone_lag1_full:  Embedding 加权同行情感 (控制变量)
#   bank_emb_sim_mean_lag1:   银行 Embedding 平均相似度 (基于 t-1 文本, 控制变量;
#                             fix omni-g-net-spill-03: 列名显式披露 lag)
# ============================================================================

# 读取 LLM 配置 (与 21_tone_llms.py 共享同一份 config.yaml 配置)
LLM_CONFIG = CONFIG.get('tone_llm_processing', {})
EMBEDDING_CONFIG = CONFIG.get('embedding_api', {})          # MAIN spec → canonical 列
# v3.7.x 双模型嵌入: ROBUSTNESS twin (shibing624/text2vec, local) → '_t2v' 列
_ROBUSTNESS_SPEC = CONFIG.get('embedding_robustness', {})
_EMB_MODELS = LLM_CONFIG.get('models', [])
_LOCAL_EMBEDDING_MODEL = None


def _embedding_config_uses_local() -> bool:
    base_url = str(EMBEDDING_CONFIG.get('base_url') or '').strip().lower()
    return base_url in {
        'local',
        'local://',
        'sentence-transformers',
        'sentence_transformers',
    }


def _encode_embeddings_local(texts, *, log_prefix="Embedding") -> np.ndarray:
    global _LOCAL_EMBEDDING_MODEL

    from sentence_transformers import SentenceTransformer

    local_model_id = (
        EMBEDDING_CONFIG.get('model')
        or 'shibing624/text2vec-base-chinese'
    )
    if _LOCAL_EMBEDDING_MODEL is None:
        logger.info(f"    {log_prefix}: 使用本地模型 {local_model_id}")
        _LOCAL_EMBEDDING_MODEL = SentenceTransformer(local_model_id)

    emb_local = _LOCAL_EMBEDDING_MODEL.encode(
        list(texts),
        batch_size=int(EMBEDDING_CONFIG.get('batch_size', 32) or 32),
        show_progress_bar=False,
    )
    return np.asarray(emb_local, dtype=np.float32)


async def _get_embeddings_api(texts, model='text-embedding-3-small', cache=None):
    """调用 OpenAI 兼容 /embeddings 端点获取文本向量（带缓存）。

    base_url 和 api_key 从 config.yaml 的 tone_llm_processing.models[0]
    读取, 与 21_tone_llms.py 共享同一份配置, 严禁硬编码。

    Args:
        texts: list[str], 待编码文本列表
        model: str, embedding 模型名称
        cache: LLMCache 实例, 用于持久化缓存

    Returns:
        np.ndarray, shape=(len(texts), dim), 归一化后的嵌入向量矩阵

    Raises:
        RuntimeError: API 返回非 200 状态码 (重试耗尽后)
    """
    import asyncio

    import aiohttp

    if EMBEDDING_CONFIG and not _embedding_config_uses_local():
        base_url = EMBEDDING_CONFIG.get('base_url', '')
        api_key = EMBEDDING_CONFIG.get('api_key', '')
        model = EMBEDDING_CONFIG.get('model') or model
    elif not _EMB_MODELS:
        raise RuntimeError("config.yaml 中无可用 LLM 模型配置")
    else:
        model_cfg = _EMB_MODELS[0]  # 使用第一个模型的 API 端点
        base_url = model_cfg.get('base_url', '')
        api_key = model_cfg.get('api_key', '')

    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {api_key}"}

    # Plan-r3 P3-17 接入: embedding 缓存键的 prompt_version 维度.
    text_pipeline_version = (
        EMBEDDING_CONFIG.get('text_pipeline_version', 'v0')
        if EMBEDDING_CONFIG else 'v0'
    )

    # 查询缓存
    cached_results = [
        cache.get(model, text, prompt_version=text_pipeline_version)
        if cache else None
        for text in texts
    ]
    missing_indices = [i for i, res in enumerate(cached_results) if res is None]
    missing_texts = [texts[i] for i in missing_indices]

    if cache and len(texts) > 0:
        logger.info(f"    缓存拦截: 命中 {len(texts) - len(missing_texts)} 条, 缺失 {len(missing_texts)} 条")

    # 调用 API 获取缺失的 embeddings
    # P-023 修复 (v3.7.1): 旧实现单次 POST, 任何 !=200 即 RuntimeError 抹除
    # in-flight batch + 已 cache 的前序 batch 写入. 现加 retry + 指数退避,
    # 镜像 strategic_diff.py:542 的 pattern. 非 retry 类 4xx 仍立即 raise.
    missing_embs = []
    if missing_texts:
        BATCH = 100  # OpenAI embeddings API 单次最多 2048 个输入
        MAX_RETRIES = 5
        RETRY_DELAY = 2.0
        MAX_RETRY_DELAY = 60.0
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(missing_texts), BATCH):
                batch_texts = missing_texts[i:i + BATCH]
                payload = {"model": model, "input": batch_texts}
                delay = RETRY_DELAY
                batch_embs = None
                for attempt in range(MAX_RETRIES):
                    try:
                        async with session.post(
                            f"{base_url}/embeddings",
                            json=payload, headers=headers,
                            timeout=aiohttp.ClientTimeout(total=120),
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                batch_embs = [
                                    item['embedding']
                                    for item in sorted(data['data'],
                                                       key=lambda x: x['index'])
                                ]
                                break
                            if resp.status in (429, 500, 502, 503, 504):
                                body = await resp.text()
                                if attempt < MAX_RETRIES - 1:
                                    logger.warning(
                                        f"    Embedding HTTP {resp.status} "
                                        f"attempt {attempt + 1}/{MAX_RETRIES}, "
                                        f"sleep {delay:.1f}s"
                                    )
                                    await asyncio.sleep(delay)
                                    delay = min(delay * 2, MAX_RETRY_DELAY)
                                    continue
                                raise RuntimeError(
                                    f"Embedding API HTTP {resp.status} "
                                    f"(重试 {MAX_RETRIES} 次耗尽): {body[:200]}"
                                )
                            # 非 retry 类 (400/401/404 等) 立即 raise
                            body = await resp.text()
                            raise RuntimeError(
                                f"Embedding API HTTP {resp.status}: {body[:200]}"
                            )
                    except aiohttp.ClientError as e:
                        if attempt < MAX_RETRIES - 1:
                            logger.warning(
                                f"    Embedding ClientError {type(e).__name__} "
                                f"attempt {attempt + 1}/{MAX_RETRIES}, "
                                f"sleep {delay:.1f}s"
                            )
                            await asyncio.sleep(delay)
                            delay = min(delay * 2, MAX_RETRY_DELAY)
                            continue
                        raise

                if batch_embs is None:
                    raise RuntimeError(
                        f"Embedding batch {i // BATCH + 1} 重试耗尽未拿到结果"
                    )
                missing_embs.extend(batch_embs)

                # 批量写入缓存
                if cache:
                    cache.put_batch(
                        model,
                        batch_texts,
                        [json.dumps(emb) for emb in batch_embs],
                        prompt_version=text_pipeline_version,
                    )

                logger.info(f"    Embedding batch {i // BATCH + 1}/"
                            f"{(len(missing_texts) - 1) // BATCH + 1} 完成")

    # 拼装最终结果
    final_embs = []
    missing_ptr = 0
    for res in cached_results:
        if res is not None:
            final_embs.append(json.loads(res))
        else:
            final_embs.append(missing_embs[missing_ptr])
            missing_ptr += 1

    return np.array(final_embs)


def _embed_peer_texts(texts, *, year, spec=None) -> np.ndarray | None:
    """Encode peer texts via the shared dual-model engine (_eng.embed_texts).

    spec 决定模型与路径 (MAIN=text-embedding-3-small / ROBUSTNESS=text2vec);
    默认 EMBEDDING_CONFIG (canonical 主轨)。本地 spec 走 sentence-transformers,
    API spec 经 LLMCache 穿透 (cache db 路径与历史实现一致)。失败/形状异常 → None。
    """
    cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
    try:
        emb_matrix = _eng.embed_texts(
            texts,
            spec or EMBEDDING_CONFIG,
            cache_db_path=cache_db,
            log_prefix=f"年份 {year}: Embedding",
        )
    except Exception as exc:
        logger.error(f"  年份 {year}: Embedding 失败 ({exc}), 跳过")
        return None

    if emb_matrix is None:
        logger.warning(f"  年份 {year}: Embedding 返回 None, 跳过")
        return None

    logger.info(f"  年份 {year}: Embedding 成功, dim={emb_matrix.shape[1]}")
    return emb_matrix


def _compute_embedding_peer_network_pass(df_exploded: pd.DataFrame,
                                         panel: pd.DataFrame,
                                         *,
                                         spec=None,
                                         suffix: str = "") -> dict:
    """单 spec 的 Embedding 同业网络构建 (一遍), 返回 (bank, year) → 指标 dict。

    suffix 在指标名上注入轨道标识 (canonical 主轨 = ""; ROBUSTNESS 稳健轨 = "_t2v"),
    插在 ``_full``/``_ctx``/``_ss`` 之类的轨道后缀之前 (无轨道后缀时直接追加在末尾):
      emb_peer_tone_lag1_full  →  emb_peer_tone_lag1{suffix}_full
      bank_emb_sim_mean_lag1   →  bank_emb_sim_mean_lag1{suffix}

    每遍用 **自己的 spec 独立嵌入** 自己的文本, 绝不混用 API(1536d)/text2vec(768d) 向量。
    维度无关 (cosine 在任意维度上都成立)。

    fix(omni-g-net-spill-02, 2026-06-11): 移除 8000 字符前缀截断 — 旧实现只嵌入
    bank-year 超级文档行序最先若干篇文章的前缀 (盘上 30.5% bank-year 被截, 被截组
    中位仅留 37.5% 文本; T=18 下退化更剧)。现把完整超级文档交 embedding_engine
    (split_text_for_embedding 分块 + 逐块 L2 归一 token 加权 mean pooling) 编码全文;
    同时拼接顺序改 docid 升序确定性排序 (旧实现依赖上游行序)。⚠ 块文本变 → API 轨
    缓存键变, 下次 production run 将对超长 bank-year 触发新 embedding 调用。

    fix(omni-g-net-spill-03, 2026-06-11): sim 列重命名 bank_emb_sim_mean →
    bank_emb_sim_mean_lag1 (及 _t2v) — 该值由 t-1 超级文档算出 (与 emb_peer_tone_lag1
    同一 sim_matrix), 旧名无 lag 标记, 与 bank_cogn_mean (当年文本) 口径混淆。
    """
    text_col = '内容'
    title_col = '标题'

    # 三轨 parity (full/ctx/ss, 原 dual-track 2026-06-08): W_emb 同业网基于文本相似度
    # (track-agnostic), 与被传播的 tone 无关 → 用同一 W_emb 同时传播 full / ctx / ss 三轨
    # tone, 零额外嵌入 ($0)。ss = 银行+金科同句共现轨 (llm_vote_tone_ss; 回退=镜像 ctx→全文
    # body)。panel 已有 llm_vote_tone_ctx/ss 可直接喂入; 缺列时各自 `in panel.columns` 守卫
    # 优雅跳过。sim_key (bank_emb_sim_mean_lag1) 是文本相似度均值, track-agnostic, 不分轨。
    _tone_tracks = [('_full', 'llm_vote_tone_full')]
    if 'llm_vote_tone_ctx' in panel.columns:
        _tone_tracks.append(('_ctx', 'llm_vote_tone_ctx'))
    if 'llm_vote_tone_ss' in panel.columns:
        _tone_tracks.append(('_ss', 'llm_vote_tone_ss'))
    sim_key = f'bank_emb_sim_mean_lag1{suffix}'  # fix(omni-g-net-spill-03, 2026-06-11)

    years = sorted(panel['year'].unique())
    emb_results = {}  # key: (bank, year), value: dict

    for year in years:
        lag_year = year - 1
        df_lag = df_exploded[df_exploded['year'] == lag_year]

        if df_lag.empty:
            logger.info(f"  年份 {year}: 滞后年 {lag_year} 无数据, 跳过")
            continue

        # fix(omni-g-net-spill-02, 2026-06-11): 超级文档拼接顺序确定性 — 旧实现
        # 依赖上游行序 (groupby 保留帧内顺序), 行序漂移 → 拼接文本漂移 → 向量漂移。
        # 按 docid (缺则 日期/标题) 稳定升序排序后再聚合。
        _sort_keys = [c for c in ('docid', '日期', '标题')
                      if c in df_lag.columns]
        if _sort_keys:
            df_lag = df_lag.sort_values(_sort_keys, kind='mergesort')

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

        # ── 2. 完整超级文档 (fix omni-g-net-spill-02: 不再 8000 字符前缀截断;
        #       超长文本由 _eng.embed_texts 内部分块 + token 加权 mean pooling) ──
        texts = list(bank_texts.values)

        # ── 3. 获取 Embedding (本 spec 独立嵌入; 经统一引擎 _eng) ──
        emb_matrix = _embed_peer_texts(texts, year=year, spec=spec)
        if emb_matrix is None:
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
        # fix(omni-g-net-spill-04, 2026-06-11): W_emb 构造前 clip 负 cosine —
        # row_stochastic_normalize 对含负项的行做行和归一会产生负"权重"
        # (加权均值语义破坏, 行和分母可被负项侵蚀至 ≤0 → 静默 NaN/符号翻转)。
        # cosine 非负性无保证 (text2vec/768d 轨与异质语料下负值可发生), 显式告警披露。
        _n_neg_sim = int((sim_matrix < 0).sum())
        if _n_neg_sim:
            logger.warning(
                f"  年份 {year}: sim_matrix 含 {_n_neg_sim} 个负 cosine, "
                f"W_emb 构造前 clip 为 0 (sim_mean 仍基于未 clip 真值)")
        sim_w = np.clip(sim_matrix, 0.0, None)
        sim_df = pd.DataFrame(sim_w, index=bank_list, columns=bank_list)
        W_emb = row_stochastic_normalize(sim_df)

        # ── 5. emb_peer_tone = W_emb(t-1) × tone(t-1), 三轨 (full/ctx/ss) 共享同一 W_emb ──
        panel_lag = panel[panel['year'] == lag_year].set_index('target_bank')
        # fix(netspill-embpeertone-fillna, metric-audit 2026-06-10 review-closure NSP-1):
        # 与 peer_tone/peer_cov 同型修复 (原 completeness-06 仅守孤立行)。嵌入网 W_emb 稠密
        # 且行随机, fillna(0) 把缺 tone 同行伪零注入分子而权重仍留在行和(=1)分母 → 在 T=18
        # 全量(缺 tone 同行有真实新闻/权重)下加权均值向 0 衰减。改为仅对 OBSERVED-tone 同行
        # 加权均值并按观测权重和重归一; denom>0 同时覆盖"有同行"(孤立行守卫)与"有观测-tone 同行"。
        # ⚠ 落盘提示 (NSP-A): 本嵌入轨依赖 30a_article_embeddings(当前缺), stage 45 未重跑嵌入
        # pass, 故盘上 emb_peer_tone 仍是旧 fillna 值、golden 暂未反映本修(repro 仍绿因二者同陈旧)。
        # T=2 上本修为近-no-op (15 个缺 tone 银行 ln_news_coverage=0 → W_emb 权重~0, 旧≈新,
        # 盘上 [0.953,0.969] 即正确值); 真实差异仅现于 T=18。落盘待带 embeddings 的 production run。
        _track_tone_vecs = {}  # track_suffix -> emb_peer_tone ndarray (按 bank_list 对齐)
        _Wemb = W_emb.values
        for _track, _tcol in _tone_tracks:
            if _tcol not in panel_lag.columns:
                continue
            tone_vec = pd.Series(np.nan, index=bank_list)
            for bank in bank_list:
                if bank in panel_lag.index:
                    val = panel_lag.loc[bank, _tcol]
                    if isinstance(val, pd.Series):
                        val = val.iloc[0]
                    tone_vec[bank] = val
            tone_arr = tone_vec.to_numpy(dtype=float)
            obs_mask = ~np.isnan(tone_arr)
            tone_obs = np.where(obs_mask, tone_arr, 0.0)
            denom = _Wemb[:, obs_mask].sum(axis=1)
            with np.errstate(invalid='ignore', divide='ignore'):
                _ept = (_Wemb @ tone_obs) / denom
            _track_tone_vecs[_track] = np.where(denom > 0, _ept, np.nan)

        for idx, bank in enumerate(bank_list):
            # 平均相似度: 该银行与所有其他银行的 Embedding 余弦相似度均值。
            # fix(omni-g-net-spill-04, 2026-06-11): 按索引排除对角 (np.delete), 而非
            # 旧 sim_row>0 符号筛选 — 旧实现把"排除对角线"与"按符号筛选"混同, 非正
            # cosine 同行被静默剔除 (实为"仅正相似度均值"), 且使 [0,1] 下界断言
            # 结构性不可触发。基于未 clip 的真实 cosine (n_banks >= 2 已守卫)。
            sim_mean = float(np.mean(np.delete(sim_matrix[idx], idx)))
            _entry = {sim_key: sim_mean}
            for _track, _ept in _track_tone_vecs.items():
                _entry[f'emb_peer_tone_lag1{suffix}{_track}'] = _ept[idx]
            emb_results[(bank, year)] = _entry

        _log_tone = _track_tone_vecs.get('_full')
        _mean_str = (f"{np.nanmean(_log_tone):.4f}"
                     if _log_tone is not None and len(_log_tone) else "n/a")
        logger.info(f"  年份 {year}: {n_banks} 家银行, "
                    f"Embedding 同行情感均值(full)={_mean_str}")

    return emb_results


def compute_embedding_peer_network(df_exploded: pd.DataFrame,
                                    panel: pd.DataFrame) -> pd.DataFrame:
    """基于 Embedding 向量相似度的同业网络控制变量 (双模型嵌入)。

    使用 Sentence Embedding 将每家银行每年的新闻文本编码为向量,
    通过余弦相似度构建动态同业网络权重矩阵, 计算加权同行情感
    作为内生性处理的控制变量。

    嵌入双模型 (v3.7.x, 与情感三轨正交的另一维): 主轨 (MAIN spec =
    text-embedding-3-small) 写 canonical 列 (emb_peer_tone_lag1_full /
    bank_emb_sim_mean_lag1); 稳健轨 (ROBUSTNESS spec = shibing624/text2vec) 用
    **各自独立的 spec 嵌入各自的文本** 写同名 + '_t2v' 列
    (emb_peer_tone_lag1_t2v_full / bank_emb_sim_mean_lag1_t2v)。稳健轨失败时其
    '_t2v' 列填 NaN 并记日志, 不影响 canonical 主轨。
    ⚠ 区分两个独立轴: ① 嵌入模型轴 (canonical / _t2v); ② 情感三轨 (full/ctx/ss,
    ss=银行+金科同句共现)。每个嵌入模型轴下, emb_peer_tone 对全部存在的情感轨
    (llm_vote_tone_full/ctx/ss) 各产一列 → emb_peer_tone_lag1{_t2v?}{_full|_ctx|_ss};
    sim_mean 是文本相似度均值, track-agnostic, 不分情感轨。

    fix(omni-g-net-spill-02/03/04, 2026-06-11): 完整超级文档分块嵌入 (去 8000 字符
    前缀截断) + sim 列加 _lag1 显式披露 t-1 文本口径 + sim_mean 按索引去对角
    (真实 cosine 域 [-1,1], 不再 sim_row>0 符号筛选)。

    方法论:
      - 权重矩阵 W_emb 基于 Embedding 余弦相似度 (负值 clip 为 0), 非二值共现
      - 滞后一期 (t-1) 避免 Manski (1993) 反射问题
      - 双模型独立嵌入 (API 1536d / text2vec 768d 绝不混用; 维度无关)

    Args:
        df_exploded: 文章级 DataFrame, 含 target_bank/year/标题/内容
        panel: 银行-年份面板 DataFrame

    Returns:
        panel: 追加 emb_peer_tone_lag1_full, bank_emb_sim_mean_lag1
               + 稳健 twin emb_peer_tone_lag1_t2v_full, bank_emb_sim_mean_lag1_t2v
               列的面板

    References:
        Hoberg, G., & Phillips, G. (2016). JPE, 124(5), 1423-1465.
        Reimers, N., & Gurevych, I. (2019). EMNLP-IJCNLP 2019.
        Manski, C. F. (1993). RES, 60(3), 531-542.
    """
    logger.info("=" * 60)
    logger.info("Embedding 同业网络控制变量 (Hoberg & Phillips 2016)")
    logger.info("=" * 60)

    tone_col = 'llm_vote_tone_full'
    if tone_col not in panel.columns:
        logger.warning(f"  {tone_col} 不存在, 跳过 Embedding 同业网络")
        return panel

    # ── 主轨 (canonical): MAIN spec → emb_peer_tone_lag1_full / bank_emb_sim_mean_lag1 ──
    emb_results = _compute_embedding_peer_network_pass(
        df_exploded, panel, spec=EMBEDDING_CONFIG, suffix="")

    if emb_results:
        emb_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1], **v}
            for k, v in emb_results.items()
        ])
        panel = panel.merge(emb_df, on=['target_bank', 'year'], how='left')

        # 范围断言 — fix(omni-g-net-spill-04, 2026-06-11): sim_mean 现为真实 cosine
        # 域 (可含负), 断言界从 [0,1] 改为 [-1,1] (旧 [0,1] 下界因 sim_row>0
        # 符号筛选结构性不可触发, 属自我掩蔽断言)。
        valid_sim = panel['bank_emb_sim_mean_lag1'].dropna()
        if len(valid_sim) > 0:
            # network-metrics-audit 2026-06-13 (N-10): 裸 assert → 显式 raise (python -O 安全),
            # 容差 1e-10→1e-6 适配 float32。值域语义不变, golden-safe。
            if not ((valid_sim >= -1 - 1e-6).all() and (valid_sim <= 1 + 1e-6).all()):
                raise ValueError(
                    f"bank_emb_sim_mean_lag1 超出 [-1,1]: "
                    f"[{valid_sim.min():.6f}, {valid_sim.max():.6f}]")
            logger.info(f"  Embedding 同业网络已合并: {len(valid_sim):,} 有效值, "
                        f"sim_mean={valid_sim.mean():.4f}")
    else:
        logger.warning("  未生成任何 Embedding 同业网络变量")

    # ── 稳健轨 (ROBUSTNESS twin): text2vec → *_t2v* 列 (失败仅填 NaN, 不阻塞主轨) ──
    # 三轨 parity (full/ctx/ss, 原 dual-track 2026-06-08): _t2v 轨复用同一 pass → 自动产
    # _full + _ctx + _ss 孪生; 失败兜底亦需对三轨同时 NaN 填充, 保持降级对称。ss 列在缺
    # llm_vote_tone_ss 时不追加 (与 _compute_embedding_peer_network_pass 的轨守卫同口径)。
    t2v_tone_cols = ['emb_peer_tone_lag1_t2v_full']
    if 'llm_vote_tone_ctx' in panel.columns:
        t2v_tone_cols.append('emb_peer_tone_lag1_t2v_ctx')
    if 'llm_vote_tone_ss' in panel.columns:
        t2v_tone_cols.append('emb_peer_tone_lag1_t2v_ss')
    t2v_sim_col = 'bank_emb_sim_mean_lag1_t2v'  # fix(omni-g-net-spill-03, 2026-06-11)
    if not _ROBUSTNESS_SPEC:
        logger.info("  无 embedding_robustness spec, 跳过 _t2v 稳健轨")
        for _c in (*t2v_tone_cols, t2v_sim_col):
            panel[_c] = np.nan
        return panel

    logger.info("-" * 60)
    logger.info("  稳健 twin: text2vec (shibing624) → _t2v 列")
    try:
        t2v_results = _compute_embedding_peer_network_pass(
            df_exploded, panel, spec=_ROBUSTNESS_SPEC, suffix="_t2v")
    except Exception as exc:
        logger.warning(f"  _t2v 稳健轨整体失败 ({exc}), 相关列填 NaN")
        t2v_results = {}

    if t2v_results:
        t2v_df = pd.DataFrame([
            {'target_bank': k[0], 'year': k[1], **v}
            for k, v in t2v_results.items()
        ])
        panel = panel.merge(t2v_df, on=['target_bank', 'year'], how='left')
        # 缺失轨道列补齐 (graceful: 某些 (bank, year) 未生成时)
        for col in (*t2v_tone_cols, t2v_sim_col):
            if col not in panel.columns:
                panel[col] = np.nan
        valid_t2v_sim = panel[t2v_sim_col].dropna()
        if len(valid_t2v_sim) > 0:
            logger.info(f"  _t2v 稳健轨已合并: {len(valid_t2v_sim):,} 有效值, "
                        f"sim_mean={valid_t2v_sim.mean():.4f}")
    else:
        logger.warning("  _t2v 稳健轨未生成任何变量, 相关列填 NaN")
        for _c in (*t2v_tone_cols, t2v_sim_col):
            panel[_c] = np.nan

    return panel
