"""
47_network_brokerage.py — 信息经纪网络与二分图中心度
=====================================================

管线位置:
  40_panel_export_main.py → 步骤 7h-brok / 7h-neg / 7h-fire
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
  → industry_neg_shock 使用 LOO 消除机械性自相关:
    即银行 i 的冲击值 = 同年其余所有银行 j≠i 的负面比率均值, 排除自身。
    ⚠ 识别更正 (2026-06-10): 同期 LOO 仅去自相关, **不**解决 Manski 反射/同时性
    (同期同行结果仍由共同冲击联合决定); 作 IV/treatment 须滞后 t-1 或工具化。
    ⚠ 年 FE 共线披露 (fix omni-g-net-brok-01, 2026-06-11): 同期 LOO 均值是
      组内常数减自身的仿射变换 shock_i,t = S_t/(N_t-1) − ratio_i,t/(N_t-1);
      含年 FE 时 S_t/(N_t-1) 被吸收, 剩余识别变异与自身 neg_ratio within-year
      精确共线 (corr = −1; Angrist 2014, The perils of peer effects)。
      → 含年 FE 的规格请改用滞后变体 industry_neg_shock_lag1。

输出变量 (Stata 回归可用):
  - brokerage_eigen_cent: 二分图特征向量中心度
    (按连通分量分别计算 + 分量内归一; 孤立点/微小分量为缺失,
     详见 _eigenvector_centrality_by_component)
    Stata 示例: reg Y brokerage_eigen_cent X, cluster(province)
  - industry_neg_shock: 行业负面冲击指数 (同期 LOO)
    ⚠ 不可与年 FE 同入 (absorb(... year) 下与自身 neg_ratio 精确共线, 见上);
      仅限无年 FE 的描述性规格。
    Stata 示例 (无年 FE): reg Y industry_neg_shock X, cluster(province)
  - industry_neg_shock_lag1: 行业负面冲击指数 (t-1 滞后, 年 FE 下保留跨期识别变异)
    Stata 示例: reghdfe Y industry_neg_shock_lag1 X, absorb(bank_id year) cluster(province)
  - brokerage_fire_sale: 经纪中心度(t-1) × 行业负面冲击(t)
    交乘项随 i×t 变异, 不受上述年 FE 完全共线影响; 但 shock 同期主效应项同染,
    主效应请用 industry_neg_shock_lag1 (见 compute_fire_sale_interaction docstring)。
    Stata 示例: reg Y c.brokerage_fire_sale X, cluster(province)
    经济含义: 正系数 → 信息枢纽银行在行业负面冲击下遭受更大声誉损失
"""

import os
import platform
import sys
import time

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
from news_process.core.logging import pct4, setup_logging, sig4

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
    # fix(network-metrics-reaudit 2026-06-13, N-10): 裸 assert 在 python -O 下被剥离 →
    # 守卫静默失效。改显式 raise, 与 network_spillover.py 两处 -O 加固同口径。
    if not nx.is_bipartite(G):
        raise ValueError(f"年份 {year}: 图不是二分图!")

    return G


# ============================================================================
# 2. 经纪中心度计算 (按连通分量)
# ============================================================================

# fix(omni-g-net-brok-02, 2026-06-11): 微小连通分量门槛 — 节点数低于该值的
# 分量 (孤立点 / 单媒体-单银行 pair) 不计算中心度, 其银行置 NaN。
# 取 3 (= 1 媒体 + 2 银行), 与全图层面的最小节点数门槛语义一致。
_MIN_COMPONENT_SIZE = 3

# 一次性 banner 守门 (本模块三个 entry fn 共享同一 47_network_brokerage 日志;
# ENV/CONFIG/METHODOLOGY 块仅在首个被 runner 调用的 entry fn 起始处 emit 一次)。
_BANNER_EMITTED = False


def _log_env_config_methodology() -> None:
    """一次性打印 项目/环境 + 运行配置 + 方法论引用 (含 DOI) 三大块。

    本模块是 panel runner (步骤 7h-brok/7h-neg/7h-fire) 调用的库函数, 三个 entry
    fn (compute_brokerage_centrality / compute_industry_neg_shock /
    compute_fire_sale_interaction) 共享 logs/47_network_brokerage.log。为避免重复,
    本 banner 经 _BANNER_EMITTED 守门, 仅在首个被调 entry fn 起始处 emit 一次。

    纯日志, 不改任何产物 / schema / 控制流 / 返回值 (golden-safe)。失败仅 warning,
    绝不让日志块崩阶段。
    """
    global _BANNER_EMITTED
    if _BANNER_EMITTED:
        return
    _BANNER_EMITTED = True
    try:
        logger.info("=" * 60)
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (信息经纪网络与二分图中心度; "
                    "panel runner 步骤 7h-brok / 7h-neg / 7h-fire)")
        logger.info("     · 项目: news_process 研究数据流水线 "
                    "(中文银行/金科新闻 → 计量面板); 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·网络·API ($0)")
        logger.info(f"     · networkx 可用: {HAS_NETWORKX} "
                    "(缺失 → 经纪中心度优雅跳过, 仅产 LOO 行业冲击)")
        logger.info("     · 确定性: 中心度走确定性迭代法 (uniform nstart, 无 BLAS/ARPACK "
                    "随机初值) → 跨 run 逐位可复现 (见 _eigenvector_centrality_by_component)")

        logger.info("  ⚙ 运行配置")
        logger.info(f"     · 微小分量门槛 _MIN_COMPONENT_SIZE={_MIN_COMPONENT_SIZE:,d} "
                    "(节点数低于此的分量银行置 NaN)")
        logger.info("     · 特征向量中心度: max_iter=2,000 | tol="
                    f"{sig4(1e-06)} | 分量内 L2 归一 | weight='weight'")
        logger.info("     · 行业负面冲击 LOO: min_count 默认=5 (单篇 {0,1} 极值守门); "
                    "同期 + t-1 滞后双变体")
        logger.info("     · 二分图银行端原生中心度 (WS-B): 5 指标 (degree/between/"
                    "closeness@LCC/clustering-ra/node-redundancy@deg>=2)")

        logger.info("  📖 方法论依据 (运行结果可对照下列文献核验)")
        logger.info("     · 二分图信息经纪网络 + 特征向量中心度: "
                    "Han, M., Kim, S. (H.), & Nanda, V. K. (2024). "
                    "Institutional brokerage networks: Facilitating liquidity "
                    "provision. The Review of Financial Studies, 37(9), "
                    "2903-2935. https://doi.org/10.1093/rfs/hhae026")
        logger.info("       (白话: 把原文『基金-券商』二分图改造为『媒体-银行』, "
                    "衡量银行在信息分发网络中的枢纽地位)")
        logger.info("     · LOO 消除机械性自相关: "
                    "Manski, C. F. (1993). Identification of endogenous social "
                    "effects: The reflection problem. The Review of Economic "
                    "Studies, 60(3), 531–542. https://doi.org/10.2307/2298123")
        logger.info("       (白话: 行业负面冲击=同年『其余』银行的负面比率均值, "
                    "排除自身→去自相关; ⚠ 同期 LOO 仍不解反射问题, "
                    "作 IV/treatment 须滞后 t-1)")
        logger.info("     · 媒体网络中心度 → 语调偏向 (近期同构应用): "
                    "Xu, G. (2024). News bias in financial journalists' social "
                    "networks. Journal of Accounting Research, 62(4), 1145–1182. "
                    "https://doi.org/10.1111/1475-679X.12560")
        logger.info("       (白话: 在金融新闻语料上建记者社会网络并以中心度解释报道"
                    "语调偏向, 与本模块『媒体-银行网络→银行端中心度→信息可见度/"
                    "语调』同构, 佐证媒体网络位置对新闻语调的解释力)")
        logger.info("     · WS-B 二分图银行端原生中心度 (度/介数/接近/聚类/冗余) 方法源①: "
                    "Freeman, L. C. (1978). Centrality in social networks conceptual "
                    "clarification. Social Networks, 1(3), 215–239. "
                    "https://doi.org/10.1016/0378-8733(78)90021-7")
        logger.info("       (白话: 中心度的概念厘清母锚 — degree/betweenness/closeness "
                    "三族的规范定义; 其中 betweenness 操作化『信息经纪』, 即银行桥接否则"
                    "不相连的媒体渠道)")
        logger.info("     · WS-B 二分图银行端原生中心度 方法源② (2-mode/双模网络专用): "
                    "Borgatti, S. P., & Everett, M. G. (1997). Network analysis of "
                    "2-mode data. Social Networks, 19(3), 243–269. "
                    "https://doi.org/10.1016/S0378-8733(96)00301-2")
        logger.info("       (白话: 媒体-银行是天然双模网络, 本文给出 2-mode 网络上度/介数/"
                    "接近/聚类/冗余的正确算法; 项目据此对银行端 5 指标做 LCC 限制 + "
                    "degree≥2 守卫, 避免单模投影丢信息)")
        logger.info("=" * 60)
    except Exception as e:  # noqa: BLE001 — 日志块绝不崩阶段
        logger.warning(f"  环境/配置/方法论 banner 输出失败 (忽略, 不影响计算): {e}")


def _eigenvector_centrality_by_component(G: 'nx.Graph', year: int) -> dict:
    """按连通分量分别计算特征向量中心度 (分量内 L2 归一)。

    fix(omni-g-net-brok-02, 2026-06-11): 旧实现在非连通图上整体跑幂迭代
    (A+I), 收敛到主分量的特征向量 — 非主分量节点的值是随迭代步数指数
    衰减的数值残渣 (盘上实测低至 3.2e-180, 同构位置跨年可差 147 个数量级),
    不具任何网络含义。现按连通分量分别计算; 孤立点/微小分量
    (< _MIN_COMPONENT_SIZE 节点) 不赋值 (上游 left join 后为 NaN)。
    ⚠ 披露: networkx 在传入子图范围内做 L2 归一 → 中心度水平仅在分量内
    可比, 跨分量比较只在"是否处于大分量"意义上成立。

    fix(omni-g-net-brok-04, 2026-06-11): 删除 nx.eigenvector_centrality_numpy
    路径 — 其底层 scipy ARPACK ``eigs()`` 不传 v0 → 随机初始向量, 同一图
    同进程重算即非逐位一致 (latent 非确定性, 全量语料连通年份会触发)。
    统一改用确定性迭代法 (uniform nstart + 纯 Python 算术, 无 BLAS/ARPACK);
    连通图 = 单分量, 与非连通图共用同一代码路径, 跨 run 逐位可复现。

    Args:
        G: 媒体-银行二分图 (节点须带 bipartite 属性)
        year: 目标年份 (仅用于日志)

    Returns:
        {node: centrality} — 仅含大分量 (>= _MIN_COMPONENT_SIZE 节点) 的
        全部节点 (媒体+银行, 调用方再筛银行节点)
    """
    vals: dict = {}
    n_tiny = 0
    for comp in nx.connected_components(G):
        if len(comp) < _MIN_COMPONENT_SIZE:
            n_tiny += 1
            continue
        sub = G.subgraph(comp)
        try:
            ec = nx.eigenvector_centrality(
                sub, weight='weight', max_iter=2000, tol=1e-06)
        except nx.PowerIterationFailedConvergence:
            # 分量内 degree 兜底 (保留旧 Level-3 语义, 仅限极端退化分量);
            # 与特征向量中心度构念不同, 故升 CRITICAL 便于事后排查
            logger.critical(
                f"  年份 {year}: {len(comp)} 节点分量幂迭代不收敛, "
                f"该分量使用 degree_centrality 兜底")
            ec = nx.degree_centrality(sub)
        vals.update(ec)
    if n_tiny:
        logger.info(f"  年份 {year}: {n_tiny} 个微小分量 "
                    f"(< {_MIN_COMPONENT_SIZE} 节点) 的银行置 NaN")
    return vals


# ============================================================================
# 2b. 二分图银行端原生中心度 (WS-B, 网络指标扩展 2026-06-21)
# ============================================================================
# 当前模块仅产 brokerage_eigen_cent (= 声望); WS-B 补 5 个二分图**原生**中心度,
# 其中 brok_bip_between_cent 才直接操作化 Han-Kim-Nanda (2024, RFS) "信息经纪"
# (银行桥接否则不相连的媒体渠道); 方法引文 Freeman (1978) / Borgatti-Everett (1997)。
# ⚠ 铁律 (执行计划 §7 WS-B / §3.1):
#   - 全部 nx.bipartite.* 返回**两端** dict → 必过滤 bank_nodes (R-D2/F6);
#   - closeness 在断连图跨分量不可比 (实测孤立点 1.5 vs 连通 1.0) → 限制到 LCC 子图 (R13);
#   - node_redundancy 对 degree<2 节点 raise NetworkXError 崩阶段 → degree>=2 预过滤铁律 (F5);
#   - 二分图 between/clustering/redundancy **丢边权** (API 约束非选择) → unweighted 拓扑经纪,
#     与加权 brokerage_eigen_cent 互补; degree 除以当年媒体数 → 年内相对 (年 FE)。

def _bipartite_bank_metrics(G: 'nx.Graph', bank_nodes: set) -> dict:
    """媒体-银行二分图银行端 5 原生中心度 (带 LCC / degree>=2 守卫)。

    Returns:
        {bank: {brok_bip_degree_cent, brok_bip_between_cent,
                brok_bip_closeness_cent, brok_bip_clustering_ra,
                brok_bip_node_redundancy}} — 仅 bank_nodes; 退化项 NaN。
    """
    out = {b: {} for b in bank_nodes}

    # 度 / 介数 (全图; 返回两端 → 过滤 bank_nodes)
    try:
        _dc = nx.bipartite.degree_centrality(G, bank_nodes)
    except Exception as e:
        logger.warning(f"  bipartite.degree_centrality 失败 ({e})"); _dc = {}
    try:
        _bc = nx.bipartite.betweenness_centrality(G, bank_nodes)
    except Exception as e:
        logger.warning(f"  bipartite.betweenness_centrality 失败 ({e})"); _bc = {}
    for b in bank_nodes:
        out[b]['brok_bip_degree_cent'] = float(_dc.get(b, np.nan))
        out[b]['brok_bip_between_cent'] = float(_bc.get(b, np.nan))

    # 聚类 (Robins-Alexander 2004, mode='dot')
    try:
        _cl = nx.bipartite.clustering(G, nodes=bank_nodes, mode='dot')
    except Exception as e:
        logger.warning(f"  bipartite.clustering 失败 ({e})"); _cl = {}
    for b in bank_nodes:
        out[b]['brok_bip_clustering_ra'] = float(_cl.get(b, np.nan))

    # 接近: 限制到最大连通分量 (R13; 否则跨分量不可比 → 排名倒挂)
    _comps = list(nx.connected_components(G))
    _lcc = max(_comps, key=len) if _comps else set()
    _clo = {}
    if len(_lcc) >= 2:
        _sub = G.subgraph(_lcc)
        _bank_lcc = {b for b in bank_nodes if b in _lcc}
        if _bank_lcc:
            try:
                _clo = nx.bipartite.closeness_centrality(_sub, _bank_lcc)
            except Exception as e:
                logger.warning(f"  bipartite.closeness 失败 ({e})"); _clo = {}
    for b in bank_nodes:
        out[b]['brok_bip_closeness_cent'] = (
            float(_clo[b]) if b in _clo else np.nan)

    # 冗余: degree>=2 预过滤铁律 (node_redundancy 对 deg<2 抛 NetworkXError)
    _elig = [b for b in bank_nodes if G.degree(b) >= 2]
    _nr = {}
    if _elig:
        try:
            _nr = nx.bipartite.node_redundancy(G, _elig)
        except Exception as e:
            logger.warning(f"  bipartite.node_redundancy 失败 ({e})"); _nr = {}
    for b in bank_nodes:
        out[b]['brok_bip_node_redundancy'] = (
            float(_nr[b]) if b in _nr else np.nan)

    return out


def compute_brokerage_centrality(
    panel: pd.DataFrame, df_exploded: pd.DataFrame
) -> pd.DataFrame:
    """计算银行在媒体-银行二分图中的特征向量中心度。

    经济含义:
      高 brokerage_eigen_cent 的银行通过更多高影响力媒体获得报道,
      意味着其信息传播范围更广、信息中介地位更高。在 Stata 回归中,
      该变量可作为银行"信息可见度"的代理变量。

    计算策略 (fix omni-g-net-brok-02/04, 2026-06-11 — 替换旧"三级 fallback"):
      按连通分量分别计算确定性迭代特征向量中心度 (分量内 L2 归一);
      孤立点/微小分量 (< _MIN_COMPONENT_SIZE 节点) 置 NaN; 分量幂迭代
      不收敛时该分量 degree_centrality 兜底 + CRITICAL 日志。
      numpy/ARPACK 路径已删除 (随机初始向量 → 跨 run 非逐位可复现),
      详见 _eigenvector_centrality_by_component docstring。

    仅提取 bipartite=1 (银行) 节点的中心度值, 排除媒体节点。

    白话: 特征向量中心度的逻辑是"你的重要性 = 你邻居重要性的加总" —
    被很多媒体报道还不够, 被**本身就连接广泛的**媒体报道才得高分
    (类似 Google PageRank)。图不连通时必须按"岛"分别算, 否则小岛上
    银行的数值只是算法的数值残渣, 没有任何网络含义。

    数据流:
      df_exploded (11_news_bank.py) → build_media_bank_bipartite()
      → nx.eigenvector_centrality → panel['brokerage_eigen_cent']

    Args:
        panel: Bank-Year 面板 DataFrame (target_bank + year 为联合键)
        df_exploded: 篇章级 DataFrame (须含 '媒体(中文)', target_bank, year)

    Returns:
        panel: 追加 brokerage_eigen_cent 列的面板 (left join, 无匹配为 NaN)
    """
    _log_env_config_methodology()

    if not HAS_NETWORKX:
        logger.warning("  networkx 未安装, 跳过经纪中心度计算")
        return panel

    _t0 = time.time()
    logger.info("=" * 60)
    logger.info("步骤 7h-brok: 信息经纪网络中心度 (Han, Kim & Nanda 2024, "
                "RFS 37(9):2903-2935; https://doi.org/10.1093/rfs/hhae026)")
    logger.info("=" * 60)

    years = sorted(panel['year'].unique())
    results = {}
    bip_results = {}   # WS-B: {(bank, year): {brok_bip_*: value}}

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

        # fix(omni-g-net-brok-02, omni-g-net-brok-04, 2026-06-11):
        # 按连通分量分别计算 (分量内归一, 微小分量 NaN), 统一确定性迭代
        # 路径 (无 ARPACK 随机初值) — 详见 _eigenvector_centrality_by_component
        comp_vals = _eigenvector_centrality_by_component(G, year)
        eigen_vals = {n: v for n, v in comp_vals.items() if n in bank_nodes}
        method_used = "component-iterative"

        for bank, val in eigen_vals.items():
            results[(bank, year)] = val

        # ─── WS-B: 二分图银行端原生中心度 (5 指标, 带守卫) ───
        for b, m in _bipartite_bank_metrics(G, bank_nodes).items():
            bip_results[(b, year)] = m

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

        valid = int(panel['brokerage_eigen_cent'].notna().sum())
        _ec = panel['brokerage_eigen_cent']
        logger.info(f"  经纪中心度已合并: {valid:,} 有效值, "
                    f"mean={sig4(_ec.mean())}")
        # 📊 关键指标解读 (运行结果信息)
        try:
            _n_rows = len(panel)
            _cov = valid / _n_rows if _n_rows else float('nan')
            logger.info(f"  📊 经纪中心度覆盖率={pct4(_cov)} "
                        f"({valid:,}/{_n_rows:,}); "
                        f"σ={sig4(_ec.std())} | min={sig4(_ec.min())} | "
                        f"max={sig4(_ec.max())}")
            # 分位数 (纯日志, golden-safe): 特征向量中心度通常右偏 (少数枢纽垄断渠道)
            _ecv = _ec.dropna()
            if len(_ecv) >= 4:
                _q = _ecv.quantile([0.25, 0.50, 0.75])
                logger.info(f"     · 分位 (有效值 n={len(_ecv):,}): p25={sig4(_q.loc[0.25])} | "
                            f"p50={sig4(_q.loc[0.50])} | p75={sig4(_q.loc[0.75])} "
                            "(右偏→少数信息枢纽银行垄断异质媒体分发渠道)")
            if valid == 0:
                logger.warning("     · ⚠ 坏: 零有效值 — 全部年份节点不足/分量过小, "
                               "下游该列无识别力 (T=2 盘面常见, 生产 T=18 应复核)")
            elif _ec.nunique(dropna=True) <= 1:
                logger.warning("     · ⚠ 坏: 退化为常量 (零方差), 下游回归无识别力")
            elif _cov < 0.5:
                logger.info("     · ⚠ 临界: 覆盖率 < 50%, 多数 Bank-Year 落在微小分量 "
                            "(< 3 节点) → NaN; 解读须注意样本选择")
            else:
                logger.info("     · ✅ 好: 覆盖率充足且有方差, 可作『信息可见度』代理变量")
        except Exception as e:  # noqa: BLE001 — 结果分析块绝不崩阶段
            logger.warning(f"  经纪中心度结果分析失败 (忽略): {e}")
    else:
        logger.warning("  未计算任何经纪中心度")

    # ─── WS-B 合并: 二分图银行端 5 中心度 (独立 left join, 镜像 brokerage_eigen 加列式) ───
    if bip_results:
        _bip_rows = []
        for (bank, yr), m in bip_results.items():
            row = {'target_bank': bank, 'year': yr}
            row.update(m)
            _bip_rows.append(row)
        _bip_df = pd.DataFrame(_bip_rows)
        panel = panel.merge(_bip_df, on=['target_bank', 'year'], how='left')
        _bcols = [c for c in _bip_df.columns
                  if c not in ('target_bank', 'year')]
        logger.info(f"  二分图银行端中心度已合并 (WS-B, Freeman 1978 / "
                    f"Borgatti-Everett 1997): {len(_bcols):,d} 列")
        for c in _bcols:
            if c in panel.columns:
                v = int(panel[c].notna().sum())
                logger.info(f"    {c}: {v:,} 有效值, mean={sig4(panel[c].mean())}")

    try:
        logger.info(f"  ⏱ 经纪中心度子步骤耗时 {sig4(time.time() - _t0)} 秒")
    except Exception:  # noqa: BLE001
        pass

    return panel


# ============================================================================
# 3. 行业负面冲击指数 (LOO)
# ============================================================================

def compute_industry_neg_shock(panel: pd.DataFrame,
                               min_count: int = 5) -> pd.DataFrame:
    """计算行业负面冲击指数 (Leave-One-Out) + t-1 滞后变体。

    经济含义:
      衡量银行 i 在年份 t 面临的"行业整体负面舆论压力",
      即同行银行的平均负面报道占比。高值表明整个行业处于
      负面舆论环境中 (如监管风暴、金融危机期间)。

    公式:
      neg_ratio_i,t = neg_count_full_i,t / n_valid_i,t   (n_valid >= min_count 守门)
      industry_neg_shock_i,t = mean_{j≠i}(neg_ratio_j,t)
      industry_neg_shock_lag1_i,t = industry_neg_shock_i,t-1

    LOO 设计动机:
      Manski, C. F. (1993). Identification of endogenous social effects:
      The reflection problem. The Review of Economic Studies, 60(3), 531-542.
      DOI: 10.2307/2298123
      → 如果直接使用行业均值 (含自身), 银行自身的负面新闻会同时
        出现在因变量和自变量中, 产生机械性相关。LOO 排除银行自身
        **消除这一机械性自相关**。
      ⚠ 识别更正 (2026-06-10): 同期 (year t) LOO **不**解决 Manski (1993) 反射/
        同时性问题 (同期同行结果仍由共同行业冲击联合决定), 不构成排他性约束的满足;
        作 IV/treatment 须滞后到 t-1 或工具化 (参 fire_sale 已正确滞后 brokerage 至 t-1)。
      ⚠ 年 FE 共线披露 (fix omni-g-net-brok-01, 2026-06-11): 同期 LOO 均值是
        组内常数减自身的仿射变换:
          shock_i,t = S_t/(N_t−1) − neg_ratio_i,t/(N_t−1),  S_t = Σ_j ratio_j,t。
        含年 FE 的回归中 S_t/(N_t−1) 被年 FE 吸收, 剩余识别变异 =
        −neg_ratio_i,t/(N_t−1), 与银行自身负面比率 within-year **精确共线**
        (corr = −1; Angrist 2014, The perils of peer effects, Labour Economics
        30, 98-108) — "行业冲击"系数实为自身比率效应的符号翻转重标度。
        → 同期水平项不可作含年 FE 规格 (项目 paper_spec 默认 [bank_fe, year_fe])
        的解释变量; 此类规格请改用本函数同时输出的 industry_neg_shock_lag1
        (年 FE 下保留跨期变异)。

    数据源 (上游管线):
      neg_count_full: 41_panel_encode_aggregate.py — LLM 投票判定为负面的文章数
      n_articles_llm_valid / n_articles: 41_panel_encode_aggregate.py — 分母篇数

    边界处理:
      - n_articles=0 → neg_ratio=NaN (通过 .replace(0, np.nan) 除零保护)
      - 有效篇数 < min_count (默认 5) → neg_ratio=NaN, 不进入行业指数
        (fix omni-g-net-brok-03, 2026-06-11: 等权 mean-of-ratios 下单篇银行的
         ratio 只能取 {0,1} 极值, 会独家设定全行业指数水平; min-n>=5 对齐项目
         惯例, 见 attention_media._ATTN_MIN_ARTICLES / encode 系 min-n 守门)
      - 自身 ratio 缺失但同年存在 >=1 家有效同行 → shock = 同行均值
        total_sum/total_n (天然 leave-out, 求和本就不含自身;
         fix omni-g-net-brok-05, 2026-06-11: 行业级变量不再与自身覆盖缺失绑定)
      - 自身有效但单银行年份 (total_n <= 1) → NaN (无法做 LOO)
      - neg_count_full 或分母列缺失 → 跳过并返回原面板
      - lag1: 按 (target_bank, year) 排序后组内 shift(1), 首年为 NaN
        (与 compute_fire_sale_interaction 的 lag 约定一致)

    Args:
        panel: Bank-Year 面板 (须含 neg_count_full, n_articles[_llm_valid])
        min_count: neg_ratio 的最小有效篇数守门 (默认 5)

    Returns:
        panel: 追加 industry_neg_shock + industry_neg_shock_lag1 列
               (∈ [0,1], NaN 表示无法计算)
    """
    _log_env_config_methodology()
    _t0 = time.time()
    logger.info("=" * 60)
    logger.info("步骤 7h-neg: 行业负面冲击指数 (LOO; Manski 1993, "
                "RES 60(3):531-542; https://doi.org/10.2307/2298123)")
    logger.info(f"  · 配置: min_count={min_count:,d} (neg_ratio 最小有效篇数守门)")
    logger.info("=" * 60)

    # no-ss-track (三轨重定位 2026-06-14, 静态枚举护栏): industry_neg_shock 是
    # **full 轨独有**的行业负面冲击 LOO — neg_count_full 自始无 ctx/ss 孪生
    # (encode 仅产 neg_count_full), 故无 _ctx 路径可镜像 → 本模块刻意不产
    # industry_neg_shock_ss / neg_count_ss。brokerage_eigen_cent / fire_sale /
    # 二分图中心度均 track-agnostic (按媒体-银行边数, 与情感轨无关), 同样无 ss 派生。
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
    # fix(omni-g-net-brok-03, 2026-06-11): 最小篇数守门 — 有效篇数 < min_count
    # 的银行 neg_ratio 置 NaN, 不进入行业指数 (防单篇 {0,1} 极值独家设定水平)
    _valid_n = panel[_nac].replace(0, np.nan).astype(float)
    _valid_n = _valid_n.where(_valid_n >= min_count)
    panel['_neg_ratio'] = panel['neg_count_full'] / _valid_n

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
            if pd.notna(own) and total_n > 1:
                # 标准 LOO: 自身有效且至少 2 家有效银行 → 排除自身取均值
                shock_vals.at[idx] = (total_sum - own) / (total_n - 1)
            elif pd.isna(own) and total_n >= 1:
                # fix(omni-g-net-brok-05, 2026-06-11): 自身 ratio 缺失时,
                # 同行均值天然 leave-out (求和本就不含自身), 行业级变量
                # 不再因自身覆盖缺失被无谓置 NaN → 避免回归 listwise 剔除
                shock_vals.at[idx] = total_sum / total_n

    panel['industry_neg_shock'] = shock_vals
    panel.drop('_neg_ratio', axis=1, inplace=True, errors='ignore')

    # fix(omni-g-net-brok-01, 2026-06-11): t-1 滞后变体 — 同期水平项在年 FE
    # 下与自身 neg_ratio 精确共线 (见 docstring), lag1 保留跨期识别变异,
    # 是含年 FE 规格的唯一可用形态。组内 shift(1) 按 index 对齐写回原行序。
    _sorted = panel.sort_values(['target_bank', 'year'])
    panel['industry_neg_shock_lag1'] = (
        _sorted.groupby('target_bank')['industry_neg_shock'].shift(1))

    valid = int(panel['industry_neg_shock'].notna().sum())
    valid_lag = int(panel['industry_neg_shock_lag1'].notna().sum())
    _sh = panel['industry_neg_shock']
    logger.info(f"  行业负面冲击已计算: {valid:,} 有效值, "
                f"mean={sig4(_sh.mean())}; "
                f"lag1: {valid_lag:,} 有效值")
    # 📊 关键指标解读: industry_neg_shock ∈ [0,1] 应为非退化分布
    try:
        if valid == 0:
            logger.warning("     · ⚠ 坏: 零有效值 — 上游 neg_count_full / 分母缺失或全 "
                           "< min_count, 行业冲击不可用")
        else:
            _smin, _smax = _sh.min(), _sh.max()
            logger.info(f"     · 分布: σ={sig4(_sh.std())} | "
                        f"min={sig4(_smin)} | max={sig4(_smax)} | "
                        f"取值域应 ∈ [0,1]")
            if _sh.nunique(dropna=True) <= 1:
                logger.warning("     · ⚠ 坏: industry_neg_shock 退化为常量 (零方差), "
                               "下游回归无识别力 (某年全 0 → 全 LOO 同值, T=2 常见)")
            elif valid_lag == 0:
                logger.info("     · ⚠ 临界: lag1 全 NaN (T 太短无 t-1) — 含年 FE 规格须用 "
                            "lag1 (同期项与自身 neg_ratio within-year 精确共线)")
            else:
                logger.info("     · ✅ 好: 同期 + lag1 双变体均有方差; 含年 FE 规格请用 "
                            "industry_neg_shock_lag1 (同期项年 FE 下精确共线)")
    except Exception as e:  # noqa: BLE001 — 结果分析块绝不崩阶段
        logger.warning(f"  行业负面冲击结果分析失败 (忽略): {e}")

    try:
        logger.info(f"  ⏱ 行业负面冲击子步骤耗时 {sig4(time.time() - _t0)} 秒")
    except Exception:  # noqa: BLE001
        pass

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

    年 FE 共线披露 (fix omni-g-net-brok-01, 2026-06-11):
      交乘项 cent_{i,t-1} × shock_{i,t} 本身**不**受同期 LOO 与年 FE 的完全
      共线影响 (cent_{i,t-1} 跨 i 变异 → 乘积保留 i×t 变异); 但 shock 的
      同期主效应项在年 FE 下与自身 neg_ratio 精确共线 (见
      compute_industry_neg_shock docstring) — 含年 FE 规格的主效应请用
      industry_neg_shock_lag1。

    Stata 回归示例 (无年 FE 时同期主效应可入; 含年 FE 请用 lag1 主效应):
      reg Y c.brokerage_fire_sale brokerage_eigen_cent industry_neg_shock X
      reghdfe Y c.brokerage_fire_sale brokerage_eigen_cent ///
          industry_neg_shock_lag1 X, absorb(bank_id year)
      → 正系数: 信息枢纽银行在行业负面冲击下遭受更大损失
      → 解释: 媒体网络放大了行业负面信息对枢纽银行的冲击

    Args:
        panel: Bank-Year 面板 (须含 brokerage_eigen_cent, industry_neg_shock)

    Returns:
        panel: 追加 brokerage_fire_sale 列
    """
    _log_env_config_methodology()
    _t0 = time.time()
    logger.info("=" * 60)
    logger.info("步骤 7h-fire: 火灾甩卖交乘项 cent(t-1) × shock(t) (Han, Kim & "
                "Nanda 2024, RFS 37(9):2903-2935; https://doi.org/10.1093/rfs/hhae026)")
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

    valid = int(panel['brokerage_fire_sale'].notna().sum())
    logger.info(f"  火灾甩卖交乘已计算: {valid:,} 有效值, "
                f"mean={sig4(panel['brokerage_fire_sale'].mean())}")

    # fix(log-audit-2026-06-20, R18): 零方差检测。盘面 T=2 下 industry_neg_shock 可能
    # 某年全 0 (如 2018), 乘积恒为常量 0 → 下游回归该列无识别力且会被 reghdfe/共线性
    # 自动剔除。显式告警, 避免"已计算 N 有效值"被误读为该交乘项可用。
    _fs = panel['brokerage_fire_sale'].dropna()
    if valid > 0 and _fs.nunique() <= 1:
        _const_val = _fs.iloc[0] if len(_fs) else float('nan')
        logger.warning(
            f"  ⚠ 坏: brokerage_fire_sale 退化为常量 (唯一值数={_fs.nunique():,d}, "
            f"min=max={sig4(_const_val)}): 零方差列下游无识别力, "
            f"疑因某年 industry_neg_shock 全 0 (T=2 盘面常见); 生产 T=18 应复核并移除该退化列。"
        )
    elif valid > 0:
        logger.info(
            f"     · ✅ 好: 交乘项随 i×t 变异 (唯一值数={_fs.nunique():,d}, "
            f"σ={sig4(_fs.std())}); 正系数 → 信息枢纽银行在行业负面冲击下遭更大损失")

    # 混淆诊断 (纯日志, golden-safe): cent(t-1) 与 shock(t) 的相关性 — 交乘模型须报告
    # 两主效应分量的共线性以避免交互系数误读 (Brambor, Clark & Golder 2006, Polit Anal)
    try:
        _lag_cs = panel.groupby('target_bank')['brokerage_eigen_cent'].shift(1)
        _corr_cs = _lag_cs.corr(panel['industry_neg_shock'])
        if pd.notna(_corr_cs):
            logger.info(
                f"     · 混淆诊断 corr(cent_t-1, shock_t)={sig4(float(_corr_cs))} "
                "(|ρ|→0 利于交乘项独立识别; 高 |ρ| 提示两主效应分量共线, 交互系数解读须谨慎)")
    except Exception as _e:  # noqa: BLE001 — 诊断块绝不崩阶段
        logger.warning(f"  火灾甩卖混淆诊断失败 (忽略): {_e}")

    try:
        logger.info(f"  ⏱ 火灾甩卖交乘子步骤耗时 {sig4(time.time() - _t0)} 秒")
    except Exception:  # noqa: BLE001
        pass

    return panel
