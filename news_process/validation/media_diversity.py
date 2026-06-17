"""
news_process.validation.media_diversity — 媒体名称与地域多样性审计

迁移说明 (Phase 7b)：
    本模块由原 root script ``38_media_diversity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.media_diversity``

=================================================

审计目标:
    量化评估新闻处理流水线各阶段数据中的媒体来源多样性和地域覆盖广度,
    从名称多样性（HHI、Shannon 熵、Gini 系数、Pielou 均匀度、层级分布）
    和地域多样性（省份/城市覆盖、集中度、区域均衡性）两个维度,
    以及时序稳定性（年际媒体构成变化）和权重覆盖诊断（未评级媒体识别）
    提供全自动化、学术级诊断报告。

分析内容:
    1. 跨阶段媒体多样性总览（含 Gini、均匀度、加权 HHI）
    2. 媒体名称多样性分析（Top-N、集中度、长尾、层级分布）
    3. 媒体地域多样性分析（省份/城市覆盖、集中度、东中西部分组）
    4. 按银行的媒体覆盖多样性（含层级加权得分、Shannon 熵）
    5. 媒体时序稳定性分析（年际 Jaccard 相似度、新进/退出媒体）
    6. 媒体权重覆盖率诊断（未评级高频媒体识别）
    7. 跨阶段差异分析（阶段间媒体存留率、指标变化量）
    8. 综合诊断结论（自动化阈值判定）

学术依据:
    [Shannon1948]  Shannon, C.E. (1948). "A Mathematical Theory of
                   Communication." Bell System Technical Journal, 27, 379–423.
                   → Shannon 熵 H = -Σ p_i log2(p_i)

    [Herfindahl1950] Herfindahl, O.C. (1950). Concentration in the Steel
                     Industry. PhD Dissertation, Columbia University.
    [Hirschman1964]  Hirschman, A.O. (1964). "The Paternity of an Index."
                     American Economic Review, 54(5), 761–762.
                     → HHI = Σ s_i², 等效数 ENM = 1/HHI

    [Pielou1966]   Pielou, E.C. (1966). "The Measurement of Diversity in
                   Different Types of Biological Collections." Journal of
                   Theoretical Biology, 13, 131–144.
                   → 均匀度 J' = H / H_max

    [Gini1912]     Gini, C. (1912). Variabilità e mutabilità. Tipografia
                   di Paolo Cuppini, Bologna.
                   → Gini 系数衡量分布不等程度

    [Bushee2010]   Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010).
                   "The Role of the Business Press as an Information
                   Intermediary." Journal of Accounting Research, 48(1), 1–19.
                   → 媒体广度 (media breadth) 作为信息环境指标

    [Tetlock2007]  Tetlock, P.C. (2007). "Giving Content to Investor
                   Sentiment: The Role of Media in the Stock Market."
                   The Journal of Finance, 62(3), 1139–1168.
                   → 新闻来源多样性与信息效率

    [Laakso1979]   Laakso, M. & Taagepera, R. (1979). "Effective Number
                   of Parties." Comparative Political Studies, 12(1), 3–27.
                   → 等效数量 ENM = 1/HHI 的方法论来源

输出:
    data/processed/eval_reports/38_media_diversity.xlsx
        - Sheet "跨阶段总览"       (含 Gini、均匀度、加权HHI 等扩展指标)
        - Sheet "全部媒体"
        - Sheet "媒体名称_Top20"
        - Sheet "媒体层级分布"
        - Sheet "长尾分析"
        - Sheet "地域分布"
        - Sheet "城市分布"
        - Sheet "银行媒体覆盖"     (含层级加权得分、Shannon 熵)
        - Sheet "未覆盖省份"
        - Sheet "时序稳定性"       (年际媒体构成变化)
        - Sheet "权重覆盖诊断"     (未评级高频媒体)
        - Sheet "跨阶段差异"       (阶段间存留率与指标变化)

设计原则:
    - 全自动化执行, 零人工参与
    - 不修改任何现有管道代码或数据
    - 所有分析结果同时输出到 Excel 和日志

白话:
    回答审稿人最爱问的"你的新闻是不是都来自一两家媒体/一两个省"。
    用一组经典集中度指标量化: HHI 越小越分散; ENM="等效几家媒体在干活";
    Shannon 熵和 Pielou 均匀度衡量报道量在各媒体间摊得匀不匀; Gini 衡量
    贫富差距式的不均; 再逐年看媒体名单变没变 (Jaccard 重叠度), 以及流水
    线每过一道筛子媒体多样性掉了多少。全部指标自动判阈值并出 Excel 报告。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 38_media_diversity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**职责**: 量化每道流水线筛子后"媒体来源"和"地域覆盖"的多样性, 回答审稿人"你的新闻是不是都来自一两家媒体/一两个省", 为论文"数据来源客观性"辩护。

**输入 (跨 6 阶段遍历)**: `00_preprocessing` / `11_bank_news` / `12_fintech_news` / `21_tone_llms` / `23_bert_tone` / `40_article_bank_level` 的 parquet; 列 `媒体(中文)` / `国家地区/省份` / `城市` / `target_bank` / `日期`。另读 config/media_weights.json (媒体权威权重, 经 load_media_weights) + config 的 mainland_china_regions。文件缺则跳过该阶段。

**处理步骤 + 算法** (每阶段):
- **媒体名称多样性** `analyze_media_names`: HHI = Σ份额²; 等效媒体数 ENM = 1/HHI (Laakso-Taagepera); **Shannon 熵** H = -Σpᵢlog₂pᵢ; **Pielou 均匀度** J' = H/log₂(N) (compute_pielou_evenness; S=1 单一媒体返回 NaN 而非误导性 1.0); **Gini 系数** (compute_gini); 加权 HHI (compute_weighted_hhi, 按权威权重); 集中率 CR1/CR3/CR5/CR10/CR20; 长尾 (仅 1 篇/≤5/≤10 的媒体数); 6 层 Tier 分布。
- **地域多样性** `analyze_regions`: 省份级 HHI/Shannon/Gini/Pielou + 东中西部分组 (国统局标准) + 城市分布 + 未覆盖省份识别 + 省份覆盖率。
- **按银行** `analyze_bank_media` (仅 40_ 阶段): 每行 media breadth (唯一媒体数, Bushee2010) + Shannon 熵 + 层级加权得分 + `Tier1-3覆盖率(%)` (权重 w≥80 视为 Tier 1-3 高权威覆盖)。
- **时序稳定性** `analyze_temporal_stability`: 逐年唯一媒体数/HHI/熵 + 新进/退出媒体 + **年际 Jaccard 相似度** (|交|/|并|, 媒体名单跨年重叠度, 平均 ≥0.7 稳定)。
- **权重覆盖诊断**: 识别高频但未评级媒体 (不在 media_weights 且非 default/其他媒体/未知), 供权重表维护。
- **跨阶段差异** `compute_cross_stage_delta`: 相邻阶段 HHI 变化率 + 媒体存留率 + Jaccard。
- **综合结论** `log_comprehensive_summary`: 对最终阶段指标自动判阈值 (HHI≥0.10 / J'<0.70 / Gini≥0.80 / 已评级报道占比<40% / 省份覆盖<80% / 地域HHI≥0.15 报警; J' 为 NaN 时不触发均匀度判定)。

所有结果汇入 12 Sheet Excel (`export_to_excel`, openpyxl)。

**外部依赖**: pandas/numpy/openpyxl。无 LLM/Embedding API, $0。

**DAG 位置**: 验证支线 stage 38, 上游 = 6 个主线阶段产出; 纯诊断终点, 不改任何管道数据。

■ 白话说明

这一步是"查新闻来源的家底": 审稿人最爱挑刺的一句话是"你的新闻是不是都来自《人民日报》一家、都报道北京一个省"。这一步就用一整套经典的"分散度"指标量化回答 —— HHI 越小说明来源越分散 (好), "等效媒体数"告诉你实际上相当于几家媒体在干活, Shannon 熵和 Pielou 均匀度衡量报道量在各家媒体间摊得匀不匀, Gini 系数衡量"贫富差距式"的不均, 还按东中西部看地域覆盖全不全。再逐年看媒体名单变没变 (Jaccard 重叠度), 以及流水线每过一道筛子、媒体多样性掉了多少。

为什么需要它: 如果数据高度集中在少数媒体或少数地区, 那"媒体关注度""媒体语调"这些核心变量就可能只反映个别媒体的口味, 而非真实舆论, 实证结论的外部有效性 (能不能推广) 就成问题。

对最终结果的影响: 它不改面板数字, 但它出的这份多样性体检报告是论文"样本代表性"段落的证据。指标健康 (来源够分散、地域够广) 就能挡住"样本有偏"的质疑; 如果发现某道筛子把多样性砍得太狠, 就提示需要回头检查那个环节是不是过度过滤了。全部自动判阈值、出一个 12 页的 Excel 报告。
========================================================================
"""

import json
import os
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/media_diversity.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_stage_summary, setup_logging

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "38_media_diversity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
EVAL_DIR = os.path.join(OUTPUT_DIR, 'eval_reports')
os.makedirs(EVAL_DIR, exist_ok=True)

FILENAMES = CONFIG.get("filenames", {})
PREPROCESSING_PARAMS = CONFIG.get("preprocessing", {})
MAINLAND_REGIONS = PREPROCESSING_PARAMS.get("mainland_china_regions", [])

# 参考文献完整引用 (供日志输出, 顺序与 docstring 一致)
REFERENCES = {
    'Shannon1948': (
        'Shannon, C.E. (1948). "A Mathematical Theory of Communication." '
        'Bell System Technical Journal, 27, 379–423.'
    ),
    'Herfindahl1950': (
        'Herfindahl, O.C. (1950). Concentration in the Steel Industry. '
        'PhD Dissertation, Columbia University.'
    ),
    'Hirschman1964': (
        'Hirschman, A.O. (1964). "The Paternity of an Index." '
        'American Economic Review, 54(5), 761–762.'
    ),
    'Pielou1966': (
        'Pielou, E.C. (1966). "The Measurement of Diversity in Different '
        'Types of Biological Collections." J. Theoretical Biology, 13, 131–144.'
    ),
    'Gini1912': (
        'Gini, C. (1912). Variabilità e mutabilità. '
        'Tipografia di Paolo Cuppini, Bologna.'
    ),
    'Bushee2010': (
        'Bushee, B.J., Core, J.E., Guay, W. & Hamm, S.J.W. (2010). '
        '"The Role of the Business Press as an Information Intermediary." '
        'Journal of Accounting Research, 48(1), 1–19.'
    ),
    'Tetlock2007': (
        'Tetlock, P.C. (2007). "Giving Content to Investor Sentiment: '
        'The Role of Media in the Stock Market." '
        'The Journal of Finance, 62(3), 1139–1168.'
    ),
    'Laakso1979': (
        'Laakso, M. & Taagepera, R. (1979). "Effective Number of Parties." '
        'Comparative Political Studies, 12(1), 3–27.'
    ),
}

# 东中西部省份分组 (国家统计局标准)
REGION_GROUPS = {
    "东部": ["北京", "天津", "河北", "辽宁", "上海", "江苏", "浙江",
             "福建", "山东", "广东", "海南"],
    "中部": ["山西", "吉林", "黑龙江", "安徽", "江西", "河南", "湖北", "湖南"],
    "西部": ["内蒙古", "广西", "重庆", "四川", "贵州", "云南", "西藏",
             "陕西", "甘肃", "青海", "宁夏", "新疆"],
}


# ============================================================================
# 2. 统计工具函数
# ============================================================================

def compute_gini(counts: np.ndarray) -> float:
    """计算 Gini 不等系数。

    参考: Gini, C. (1912). Variabilità e mutabilità.

    Gini 系数衡量分布的不等程度, 范围 [0, 1]:
      0 = 完全均匀 (所有媒体报道数相同)
      1 = 完全集中 (所有报道来自一家媒体)

    Args:
        counts: 各媒体的报道数数组。

    Returns:
        float: Gini 系数。
    """
    if len(counts) == 0 or counts.sum() == 0:
        return 0.0
    sorted_counts = np.sort(counts).astype(float)
    n = len(sorted_counts)
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * sorted_counts) / (n * sorted_counts.sum())) - (n + 1) / n)


def compute_pielou_evenness(shannon: float, n_unique: int) -> float:
    """计算 Pielou 均匀度 J'。

    参考: Pielou, E.C. (1966). J. Theoretical Biology, 13, 131–144.

    J' = H / H_max, 其中 H_max = log2(N)
    范围 [0, 1]: 1 = 完全均匀, 0 = 完全集中

    fix(omni-g-val-robust-05, 2026-06-11): S=1 (单一类别) 时 J' = H/log2(1) = 0/0
    数学未定义 (生态学惯例报 NaN/不适用)。旧实现为绕开除零硬编码返回 1.0,
    把"被单一媒体完全垄断"报成"完全均匀" (J' 语义上界), 与同报告 HHI=1.0 /
    ENM=1 的"完全集中"判读自相矛盾 — 改返回 NaN, 下游报告显示 n/a。

    Args:
        shannon:  Shannon 熵值。
        n_unique: 唯一类别数。

    Returns:
        float: Pielou 均匀度; n_unique <= 1 时返回 NaN (J' 不适用)。
    """
    if n_unique <= 1:
        return float('nan')
    h_max = np.log2(n_unique)
    return float(shannon / h_max) if h_max > 0 else float('nan')


def compute_weighted_hhi(counts: pd.Series, weights: dict,
                         default_weight: int) -> float:
    """计算权重调整 HHI。

    按媒体权重对报道数进行加权后计算 HHI, 用于评估
    高权威媒体覆盖的集中程度。

    Args:
        counts:         媒体名称 -> 报道数 的 Series。
        weights:        媒体权重字典。
        default_weight: 默认权重。

    Returns:
        float: 加权 HHI。
    """
    weighted = []
    for name, count in counts.items():
        w = weights.get(name, default_weight)
        weighted.append(count * w)
    weighted = np.array(weighted, dtype=float)
    total = weighted.sum()
    if total == 0:
        return 0.0
    shares = weighted / total
    return float(np.sum(shares ** 2))


# ============================================================================
# 3. 加载媒体权重配置
# ============================================================================

def load_media_weights() -> dict:
    """从 config/media_weights.json 加载媒体权重评分表。

    Returns:
        dict: {媒体名称: 权重分数}，排除注释键。
    """
    filepath = CONFIG["paths"]["media_weights_file"]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        weights = {k: v for k, v in raw.items() if not k.startswith("//")}
        logger.info(f"已加载 {len(weights)} 条媒体权重 ({filepath})")
        return weights
    except Exception as e:
        logger.error(f"媒体权重文件加载失败: {e}")
        return {"default": 10}


def get_tier(weight: int) -> str:
    """根据权重值返回媒体层级名称。"""
    if weight >= 100:
        return "Tier 1 (中央级, 100)"
    elif weight >= 90:
        return "Tier 2 (省部级/政策, 90-99)"
    elif weight >= 80:
        return "Tier 3 (都市/行业, 80-89)"
    elif weight >= 70:
        return "Tier 4 (地市/行业, 70-79)"
    elif weight >= 60:
        return "Tier 5 (地方/其他, 60-69)"
    else:
        return "Tier 6 (未评级/默认, <60)"


# ============================================================================
# 4. 媒体名称多样性分析
# ============================================================================

def analyze_media_names(df: pd.DataFrame, stage_name: str,
                        media_weights: dict, default_weight: int,
                        media_col: str = '媒体(中文)') -> dict:
    """分析媒体名称多样性。

    计算指标体系:
      - HHI (Herfindahl 1950): 集中度指数
      - ENM = 1/HHI (Laakso & Taagepera 1979): 等效媒体数
      - Shannon 熵 (Shannon 1948): 信息论多样性
      - Pielou 均匀度 J' (Pielou 1966): 标准化均匀度
      - Gini 系数 (Gini 1912): 分布不等程度
      - 加权 HHI: 按媒体权重加权的集中度
      - Top-k 集中率: CR1, CR3, CR5, CR10, CR20

    Args:
        df:             待分析的 DataFrame。
        stage_name:     阶段标识名。
        media_weights:  媒体权重字典。
        default_weight: 未收录媒体的默认权重。
        media_col:      媒体名称列名。

    Returns:
        dict: 包含 all_media_df, top20_df, tier_df, tail_df, metrics 等。
    """
    result = {}
    if media_col not in df.columns:
        logger.warning(f"  [{stage_name}] 缺少列 '{media_col}'，跳过媒体名称分析")
        return result

    media_series = df[media_col].fillna("未知").astype(str)
    n_unique = media_series.nunique()
    total = len(media_series)
    media_counts = media_series.value_counts()

    logger.info(f"  唯一媒体数量: {n_unique}")

    # --- 全量媒体名单 ---
    all_media_rows = []
    for i, (name, count) in enumerate(media_counts.items()):
        pct = count / total * 100
        weight = media_weights.get(name, default_weight)
        tier = get_tier(weight)
        all_media_rows.append({
            "阶段": stage_name, "排名": i + 1, "媒体名称": name,
            "报道数": count, "占比(%)": round(pct, 2),
            "权重": weight, "层级": tier,
        })
    result["all_media_df"] = pd.DataFrame(all_media_rows)
    logger.info(f"  全部媒体: {len(all_media_rows)} 家")

    # --- Top 20 ---
    top20_rows = all_media_rows[:20]
    logger.info(f"  Top 20 媒体 (按报道数量):")
    for row in top20_rows:
        logger.info(f"    {row['排名']:2d}. {row['媒体名称']:<18s} | {row['报道数']:>6,} 篇 "
                     f"({row['占比(%)']:5.2f}%) | 权重={row['权重']} | {row['层级']}")
    result["top20_df"] = pd.DataFrame(top20_rows)

    # --- 集中度指标体系 ---
    shares = media_counts / total
    hhi = float((shares ** 2).sum())
    enm = 1.0 / hhi if hhi > 0 else n_unique  # 等效媒体数
    cr1 = media_counts.head(1).sum() / total
    cr3 = media_counts.head(3).sum() / total
    top5_share = media_counts.head(5).sum() / total
    top10_share = media_counts.head(10).sum() / total
    top20_share = media_counts.head(20).sum() / total
    shannon = max(0.0, float(-np.sum(shares * np.log2(shares + 1e-15))))
    # fix(omni-g-val-robust-05, 2026-06-11): S=1 时 H_max = log2(1) = 0 (真值),
    # 旧实现显示 1.0 与 Pielou 硬编码 1.0 同源, 一并改为真值 0.0。
    shannon_max = float(np.log2(n_unique)) if n_unique > 1 else 0.0
    evenness = compute_pielou_evenness(shannon, n_unique)
    gini = compute_gini(media_counts.values.astype(float))
    w_hhi = compute_weighted_hhi(media_counts, media_weights, default_weight)

    logger.info(f"  集中度指标体系:")
    logger.info(f"    [Shannon1948] Shannon 熵 H: {shannon:.4f} (最大={shannon_max:.4f})")
    logger.info(f"      H 越高 = 媒体来源越多样化。H_max = log2(N) = 完全均匀时的熵值。")
    logger.info(f"    [Pielou1966] 均匀度 J': {evenness:.4f}")
    logger.info(f"      J' = H/H_max, 范围[0,1], 越接近1 = 报道数在各媒体间越均匀。")
    logger.info(f"    [Herfindahl1950] HHI: {hhi:.6f}")
    logger.info(f"      HHI ∈ (0,1], <0.01=高度分散, 0.01-0.15=适度集中, >0.25=高度集中。")
    logger.info(f"    [Laakso1979] 等效媒体数 ENM = 1/HHI: {enm:.1f}")
    logger.info(f"      ENM 表示'如果所有媒体均匀报道, 等效于 {enm:.0f} 家媒体在工作'。")
    logger.info(f"    [Gini1912] Gini 系数: {gini:.4f}")
    logger.info(f"      Gini ∈ [0,1], 越接近0=越均匀, 越接近1=越集中于少数媒体。")
    logger.info(f"    加权 HHI (按媒体权威权重): {w_hhi:.6f}")
    logger.info(f"      利用 media_weights.json 权重对报道数加权后计算的集中度。")
    logger.info(f"    集中率:")
    logger.info(f"      CR1={cr1:.2%} | CR3={cr3:.2%} | CR5={top5_share:.2%} "
                 f"| CR10={top10_share:.2%} | CR20={top20_share:.2%}")
    logger.info(f"    媒体报道数: 均值={media_counts.mean():.1f}, "
                 f"中位数={media_counts.median():.0f}, 标准差={media_counts.std():.1f}")

    result["metrics"] = {
        "阶段": stage_name, "总行数": total, "唯一媒体数": n_unique,
        "HHI": round(hhi, 6), "等效媒体数ENM": round(enm, 1),
        "Top1占比": round(cr1, 4), "Top3占比": round(cr3, 4),
        "Top5占比": round(top5_share, 4),
        "Top10占比": round(top10_share, 4), "Top20占比": round(top20_share, 4),
        "Shannon熵": round(shannon, 4), "Shannon熵最大值": round(shannon_max, 4),
        "Pielou均匀度": round(evenness, 4),
        "Gini系数": round(gini, 4),
        "加权HHI": round(w_hhi, 6),
    }

    # --- 长尾分析 ---
    n_one = int((media_counts == 1).sum())
    n_le5 = int((media_counts <= 5).sum())
    n_le10 = int((media_counts <= 10).sum())
    logger.info(f"  长尾分析:")
    logger.info(f"    仅 1 篇: {n_one} ({n_one/n_unique*100:.1f}%)")
    logger.info(f"    <=5 篇: {n_le5} ({n_le5/n_unique*100:.1f}%)")
    logger.info(f"    <=10 篇: {n_le10} ({n_le10/n_unique*100:.1f}%)")
    result["tail_df"] = pd.DataFrame([{
        "阶段": stage_name,
        "仅1篇媒体数": n_one, "仅1篇占比(%)": round(n_one / n_unique * 100, 1),
        "<=5篇媒体数": n_le5, "<=5篇占比(%)": round(n_le5 / n_unique * 100, 1),
        "<=10篇媒体数": n_le10, "<=10篇占比(%)": round(n_le10 / n_unique * 100, 1),
    }])

    # --- 层级分布 ---
    tier_counter = Counter()
    tier_article_counter = Counter()
    for name, count in media_counts.items():
        weight = media_weights.get(name, default_weight)
        tier = get_tier(weight)
        tier_counter[tier] += 1
        tier_article_counter[tier] += count

    tier_rows = []
    logger.info(f"  按媒体层级分布:")
    for tier in sorted(tier_counter.keys()):
        n_media = tier_counter[tier]
        n_articles = tier_article_counter[tier]
        pct = n_articles / total * 100
        logger.info(f"    {tier:<35s} | {n_media:>5} 家 | "
                     f"{n_articles:>6,} 篇 ({pct:.2f}%)")
        tier_rows.append({
            "阶段": stage_name, "层级": tier,
            "媒体数": n_media, "报道数": n_articles,
            "占比(%)": round(pct, 2),
        })
    result["tier_df"] = pd.DataFrame(tier_rows)

    # --- 权重覆盖统计 (Tier 1-5 vs Tier 6) ---
    rated_media = sum(1 for t, c in tier_counter.items() if "Tier 6" not in t)
    rated_articles = sum(c for t, c in tier_article_counter.items() if "Tier 6" not in t)
    unrated_media = tier_counter.get("Tier 6 (未评级/默认, <60)", 0)
    unrated_articles = tier_article_counter.get("Tier 6 (未评级/默认, <60)", 0)
    rated_media_pct = rated_media / n_unique * 100 if n_unique > 0 else 0
    rated_article_pct = rated_articles / total * 100 if total > 0 else 0
    logger.info(f"  权重覆盖统计 [Bushee2010]:")
    logger.info(f"    已评级 (Tier 1-5): {rated_media} 家 ({rated_media_pct:.1f}%) "
                 f"| {rated_articles:,} 篇 ({rated_article_pct:.1f}%)")
    logger.info(f"    未评级 (Tier 6):   {unrated_media} 家 "
                 f"| {unrated_articles:,} 篇")
    result["metrics"]["已评级媒体占比(%)"] = round(rated_media_pct, 1)
    result["metrics"]["已评级报道占比(%)"] = round(rated_article_pct, 1)

    return result


# ============================================================================
# 5. 媒体地域多样性分析
# ============================================================================

def analyze_regions(df: pd.DataFrame, stage_name: str,
                    region_col: str = '国家地区/省份',
                    city_col: str = '城市') -> dict:
    """分析媒体地域多样性。

    分析维度:
      - 省份级频率分布与集中度 (HHI, Shannon, Gini, Pielou)
      - 东/中/西部大区域分组统计
      - 城市级分布
      - 未覆盖省份识别
      - 省份覆盖率 = 覆盖数 / 期望数

    Args:
        df:         待分析的 DataFrame。
        stage_name: 阶段标识名。
        region_col: 地域列名。
        city_col:   城市列名。

    Returns:
        dict: 包含 region_df, city_df, metrics, uncovered_df 等。
    """
    result = {}

    # --- 省份级别 ---
    if region_col in df.columns:
        region_series = df[region_col].fillna("未知").astype(str).str.strip()
        n_unique = region_series.nunique()
        total = len(region_series)
        region_counts = region_series.value_counts()

        logger.info(f"  唯一地域数量: {n_unique}")

        region_rows = []
        cumulative = 0
        logger.info(f"  省份分布 (按报道数量):")
        for name, count in region_counts.items():
            pct = count / total * 100
            cumulative += pct
            logger.info(f"    {name:<12s} | {count:>6,} 篇 ({pct:5.2f}%) "
                         f"累计 {cumulative:5.1f}%")
            region_rows.append({
                "阶段": stage_name, "地域": name,
                "报道数": count, "占比(%)": round(pct, 2),
                "累计占比(%)": round(cumulative, 2),
            })
        result["region_df"] = pd.DataFrame(region_rows)

        # 地域集中度指标体系
        region_shares = region_counts / total
        region_hhi = float((region_shares ** 2).sum())
        region_enr = 1.0 / region_hhi if region_hhi > 0 else n_unique
        top3_share = region_counts.head(3).sum() / total
        region_shannon = max(0.0, float(-np.sum(region_shares * np.log2(region_shares + 1e-15))))
        # fix(omni-g-val-robust-05, 2026-06-11): S=1 时 H_max 真值 = 0, 与媒体名称段同步
        region_shannon_max = float(np.log2(n_unique)) if n_unique > 1 else 0.0
        region_evenness = compute_pielou_evenness(region_shannon, n_unique)
        region_gini = compute_gini(region_counts.values.astype(float))

        logger.info(f"  地域集中度指标体系:")
        logger.info(f"    HHI: {region_hhi:.6f} | 等效地域数 ENR: {region_enr:.1f}")
        logger.info(f"    Top 3 占比: {top3_share:.2%}")
        logger.info(f"    Shannon 熵: {region_shannon:.4f} "
                     f"(最大={region_shannon_max:.4f})")
        logger.info(f"    Pielou 均匀度: {region_evenness:.4f}")
        logger.info(f"    Gini 系数: {region_gini:.4f}")

        result["region_metrics"] = {
            "唯一地域数": n_unique, "地域HHI": round(region_hhi, 6),
            "地域等效数ENR": round(region_enr, 1),
            "Top3占比": round(top3_share, 4),
            "地域Shannon熵": round(region_shannon, 4),
            "地域Shannon熵最大值": round(region_shannon_max, 4),
            "地域Pielou均匀度": round(region_evenness, 4),
            "地域Gini系数": round(region_gini, 4),
        }

        # --- 东中西部大区域分组 ---
        logger.info(f"  东/中/西部大区域分组统计:")
        for group_name, provinces in REGION_GROUPS.items():
            group_count = sum(region_counts.get(p, 0) for p in provinces)
            group_pct = group_count / total * 100 if total > 0 else 0
            n_covered = sum(1 for p in provinces if p in region_counts.index)
            logger.info(f"    {group_name}: {group_count:>6,} 篇 ({group_pct:5.1f}%) "
                         f"| 覆盖 {n_covered}/{len(provinces)} 省")
            result["region_metrics"][f"{group_name}报道占比"] = round(group_pct, 2)

        # 未覆盖省份
        covered = set(region_counts.index)
        expected = set(r for r in MAINLAND_REGIONS if r != "中国")
        uncovered = sorted(expected - covered)
        coverage_rate = 1 - len(uncovered) / len(expected) if expected else 1.0
        if uncovered:
            logger.info(f"  未覆盖省份 ({len(uncovered)}):")
            for p in uncovered:
                logger.info(f"    - {p}")
        logger.info(f"  省份覆盖率: {len(expected) - len(uncovered)}/{len(expected)} "
                     f"= {coverage_rate:.1%}")
        result["region_metrics"]["省份覆盖率"] = round(coverage_rate, 4)
        result["uncovered_df"] = pd.DataFrame([
            {"阶段": stage_name, "未覆盖省份": p} for p in uncovered
        ]) if uncovered else pd.DataFrame()
    else:
        logger.warning(f"  [{stage_name}] 缺少列 '{region_col}'，跳过地域分析")

    # --- 城市级别 ---
    if city_col in df.columns:
        city_series = df[city_col].fillna("").astype(str).str.strip()
        city_series = city_series[city_series != ""]
        if len(city_series) > 0:
            n_cities = city_series.nunique()
            city_counts = city_series.value_counts()
            total_city = len(city_series)

            logger.info(f"  唯一城市数量: {n_cities}")

            city_rows = []
            logger.info(f"  全部城市分布 ({n_cities} 个):")
            for name, count in city_counts.items():
                pct = count / total_city * 100
                logger.info(f"    {name:<12s} | {count:>6,} 篇 ({pct:5.2f}%)")
                city_rows.append({
                    "阶段": stage_name, "城市": name,
                    "报道数": count, "占比(%)": round(pct, 2),
                })
            result["city_df"] = pd.DataFrame(city_rows)
            result["n_cities"] = n_cities

    return result


# ============================================================================
# 6. 按银行的媒体覆盖多样性分析
# ============================================================================

def analyze_bank_media(df: pd.DataFrame, media_weights: dict,
                       default_weight: int,
                       media_col: str = '媒体(中文)') -> pd.DataFrame:
    """分析按银行的媒体覆盖多样性。

    分析维度 (每银行):
      - 唯一媒体数 [Bushee2010: media breadth]
      - Shannon 熵 [Shannon1948]
      - 层级加权得分 = Σ(权重_i × 报道数_i) / 总报道数
      - Tier 1-3 高权威媒体覆盖率

    Args:
        df:             含 target_bank 和媒体列的 DataFrame。
        media_weights:  媒体权重字典。
        default_weight: 默认权重。
        media_col:      媒体名称列名。

    Returns:
        pd.DataFrame: 各银行的多维媒体覆盖分析。
    """
    if 'target_bank' not in df.columns or media_col not in df.columns:
        logger.warning("  缺少 target_bank 或媒体列，跳过按银行分析")
        return pd.DataFrame()

    rows = []
    for bank, group in df.groupby('target_bank'):
        media_series = group[media_col].fillna("未知").astype(str)
        n_unique = media_series.nunique()
        total = len(media_series)
        counts = media_series.value_counts()

        # Shannon 熵
        shares = counts / total
        bank_shannon = max(0.0, float(-np.sum(shares * np.log2(shares + 1e-15))))

        # 层级加权得分
        weighted_sum = 0
        tier13_count = 0
        for name, count in counts.items():
            w = media_weights.get(name, default_weight)
            weighted_sum += w * count
            if w >= 80:  # Tier 1-3
                tier13_count += count
        weighted_score = weighted_sum / total if total > 0 else 0
        tier13_pct = tier13_count / total * 100 if total > 0 else 0

        rows.append({
            '银行': bank,
            '唯一媒体数': n_unique,
            '报道总数': total,
            'Shannon熵': round(bank_shannon, 4),
            '层级加权得分': round(weighted_score, 1),
            'Tier1-3覆盖率(%)': round(tier13_pct, 1),
        })

    bank_df = pd.DataFrame(rows).sort_values('唯一媒体数', ascending=False)

    logger.info(f"  按银行的媒体多样性 ({len(bank_df)} 家银行):")
    logger.info(f"  {'银行':<25s} | {'媒体数':>5s} | {'Shannon':>7s} | "
                 f"{'加权得分':>7s} | {'T1-3(%)':>7s}")
    logger.info(f"  {'-'*70}")
    for _, row in bank_df.iterrows():
        logger.info(f"    {row['银行']:<25s} | {row['唯一媒体数']:>4} 家 | "
                     f"{row['Shannon熵']:>7.3f} | {row['层级加权得分']:>7.1f} | "
                     f"{row['Tier1-3覆盖率(%)']:>6.1f}%")

    # 描述性统计
    logger.info(f"  银行媒体多样性汇总统计:")
    logger.info(f"    唯一媒体数: mean={bank_df['唯一媒体数'].mean():.1f}, "
                 f"median={bank_df['唯一媒体数'].median():.0f}, "
                 f"std={bank_df['唯一媒体数'].std(ddof=0):.1f}")
    logger.info(f"    Shannon 熵: mean={bank_df['Shannon熵'].mean():.3f}, "
                 f"median={bank_df['Shannon熵'].median():.3f}")
    logger.info(f"    层级加权得分: mean={bank_df['层级加权得分'].mean():.1f}, "
                 f"median={bank_df['层级加权得分'].median():.1f}")

    return bank_df


# ============================================================================
# 7. 媒体时序稳定性分析
# ============================================================================

def analyze_temporal_stability(df: pd.DataFrame, stage_name: str,
                               media_weights: dict = None,
                               default_weight: int = 10,
                               media_col: str = '媒体(中文)') -> pd.DataFrame:
    """按年份追踪媒体构成变化, 检测时序稳定性。

    分析维度:
      - 每年唯一媒体数、HHI、Shannon 熵、Pielou 均匀度
      - 新进入媒体数 / 退出媒体数 (与前一年比较)
      - 年际 Jaccard 相似度 (媒体名单两年间的重叠度)

    Args:
        df:             待分析的 DataFrame (需含 '日期' 列)。
        stage_name:     阶段标识名。
        media_weights:  [预留] 媒体权重字典，当前未使用，
                        为未来按年加权 HHI 扩展预留。
        default_weight: [预留] 默认权重，当前未使用。
        media_col:      媒体名称列名。

    Returns:
        pd.DataFrame: 年度时序稳定性指标。
    """
    if '日期' not in df.columns or media_col not in df.columns:
        logger.warning(f"  [{stage_name}] 缺少日期或媒体列，跳过时序分析")
        return pd.DataFrame()

    df_t = df.copy()
    df_t['_year'] = pd.to_datetime(df_t['日期'], errors='coerce').dt.year
    df_t = df_t.dropna(subset=['_year'])
    df_t['_year'] = df_t['_year'].astype(int)

    years = sorted(df_t['_year'].unique())
    if len(years) < 2:
        logger.info(f"  [{stage_name}] 仅有 {len(years)} 个年份，跳过时序分析")
        return pd.DataFrame()

    prev_media_set = None
    rows = []

    for yr in years:
        yr_df = df_t[df_t['_year'] == yr]
        media_series = yr_df[media_col].fillna("未知").astype(str)
        n_unique = media_series.nunique()
        total = len(media_series)
        counts = media_series.value_counts()
        current_set = set(counts.index)

        shares = counts / total
        hhi = float((shares ** 2).sum())
        shannon = max(0.0, float(-np.sum(shares * np.log2(shares + 1e-15))))
        evenness = compute_pielou_evenness(shannon, n_unique)

        # 年际变化
        if prev_media_set is not None:
            new_in = len(current_set - prev_media_set)
            dropped = len(prev_media_set - current_set)
            intersection = len(current_set & prev_media_set)
            union = len(current_set | prev_media_set)
            jaccard = intersection / union if union > 0 else 0
        else:
            new_in, dropped, jaccard = 0, 0, np.nan  # 首年无前置对比

        rows.append({
            '阶段': stage_name, '年份': yr, '报道数': total,
            '唯一媒体数': n_unique, 'HHI': round(hhi, 6),
            'Shannon熵': round(shannon, 4),
            'Pielou均匀度': round(evenness, 4),
            '新进入媒体': new_in, '退出媒体': dropped,
            'Jaccard相似度': round(jaccard, 4),
        })
        prev_media_set = current_set

    trend_df = pd.DataFrame(rows)

    logger.info(f"  时序稳定性 ({years[0]}-{years[-1]}):")
    for _, r in trend_df.iterrows():
        jac_str = f"Jaccard={r['Jaccard相似度']:.3f}" if r['Jaccard相似度'] > 0 else "—"
        logger.info(f"    {int(r['年份'])}: {r['报道数']:>5,} 篇 | "
                     f"媒体={r['唯一媒体数']:>3} | HHI={r['HHI']:.4f} | "
                     f"J'={r['Pielou均匀度']:.3f} | "
                     f"+{r['新进入媒体']}/-{r['退出媒体']} | {jac_str}")

    # 趋势判断
    if len(trend_df) >= 3:
        jac_values = trend_df['Jaccard相似度'].iloc[1:].values
        avg_jac = np.mean(jac_values) if len(jac_values) > 0 else 0
        if avg_jac >= 0.7:
            logger.info(f"  ✓ 平均 Jaccard={avg_jac:.3f} ≥ 0.70, 媒体构成跨年稳定")
        elif avg_jac >= 0.5:
            logger.info(f"  ℹ️  平均 Jaccard={avg_jac:.3f}, 媒体构成有一定变动")
        else:
            logger.info(f"  平均 Jaccard={avg_jac:.3f} < 0.50, 媒体构成跨年变动较大")

    return trend_df


# ============================================================================
# 8. 权重覆盖率诊断
# ============================================================================

def analyze_weight_coverage(media_counts: pd.Series, stage_name: str,
                            media_weights: dict,
                            default_weight: int) -> pd.DataFrame:
    """诊断实际出现的媒体中有多少被 media_weights.json 收录。

    识别高频但未评级的媒体, 为权重表维护提供依据。

    Args:
        media_counts:   媒体名称 -> 报道数 的 Series。
        stage_name:     阶段标识名。
        media_weights:  媒体权重字典。
        default_weight: 默认权重。

    Returns:
        pd.DataFrame: 未评级高频媒体清单。
    """
    unrated_rows = []
    for name, count in media_counts.items():
        if name not in media_weights and name not in ("default", "其他媒体", "未知"):
            unrated_rows.append({
                "阶段": stage_name, "媒体名称": name,
                "报道数": count, "当前权重": default_weight,
                "建议": "建议补充评级" if count >= 5 else "低频可忽略",
            })

    unrated_df = pd.DataFrame(unrated_rows)
    if not unrated_df.empty:
        unrated_df = unrated_df.sort_values('报道数', ascending=False)

    n_suggest = len(unrated_df[unrated_df['建议'] == '建议补充评级']) if not unrated_df.empty else 0

    logger.info(f"  权重覆盖率诊断 [{stage_name}]:")
    logger.info(f"    未评级媒体总数: {len(unrated_df)}")
    logger.info(f"    其中报道≥5篇 (建议补充): {n_suggest}")
    if n_suggest > 0:
        logger.info(f"    高频未评级媒体 Top-10:")
        for _, r in unrated_df.head(10).iterrows():
            logger.info(f"      {r['媒体名称']:<20s} | {r['报道数']:>5,} 篇 | {r['建议']}")

    return unrated_df


# ============================================================================
# 9. 跨阶段差异分析
# ============================================================================

def compute_cross_stage_delta(overview_rows: list,
                              stage_media_sets: dict) -> pd.DataFrame:
    """计算相邻阶段间的多样性指标变化与媒体存留率。

    Args:
        overview_rows:    各阶段的总览指标列表。
        stage_media_sets: {阶段名: set(媒体名称)} 字典。

    Returns:
        pd.DataFrame: 跨阶段差异表。
    """
    if len(overview_rows) < 2:
        return pd.DataFrame()

    delta_rows = []
    for i in range(1, len(overview_rows)):
        prev = overview_rows[i - 1]
        curr = overview_rows[i]
        prev_stage = prev.get("阶段", "?")
        curr_stage = curr.get("阶段", "?")

        # 指标变化
        prev_hhi = prev.get("HHI", 0) or 0
        curr_hhi = curr.get("HHI", 0) or 0
        hhi_delta = curr_hhi - prev_hhi
        hhi_pct = hhi_delta / prev_hhi * 100 if prev_hhi != 0 else 0

        prev_n = prev.get("唯一媒体数", 0) or 0
        curr_n = curr.get("唯一媒体数", 0) or 0

        # 媒体存留率
        prev_set = stage_media_sets.get(prev_stage, set())
        curr_set = stage_media_sets.get(curr_stage, set())
        if prev_set and curr_set:
            retention = len(prev_set & curr_set) / len(prev_set) if prev_set else 0
            jaccard = (len(prev_set & curr_set) / len(prev_set | curr_set)
                       if (prev_set | curr_set) else 0)
        else:
            retention, jaccard = 0, 0

        delta_rows.append({
            "从阶段": prev_stage, "到阶段": curr_stage,
            "媒体数变化": curr_n - prev_n,
            "HHI变化": round(hhi_delta, 6),
            "HHI变化率(%)": round(hhi_pct, 2),
            "媒体存留率": round(retention, 4),
            "Jaccard相似度": round(jaccard, 4),
        })

    delta_df = pd.DataFrame(delta_rows)

    logger.info("")
    logger.info("=" * 70)
    logger.info("  跨阶段媒体多样性差异分析")
    logger.info("=" * 70)
    for _, r in delta_df.iterrows():
        logger.info(f"  {r['从阶段'][:20]:<20s} → {r['到阶段'][:20]:<20s}")
        logger.info(f"    媒体数变化: {r['媒体数变化']:+d} | "
                     f"HHI变化: {r['HHI变化']:+.6f} ({r['HHI变化率(%)']:+.1f}%)")
        logger.info(f"    媒体存留率: {r['媒体存留率']:.2%} | "
                     f"Jaccard相似度: {r['Jaccard相似度']:.4f}")
        if abs(r['HHI变化率(%)']) > 20:
            logger.info(f"    HHI 变化超过 20%, 该阶段对媒体集中度影响显著")

    return delta_df


# ============================================================================
# 10. 综合诊断结论
# ============================================================================

def log_comprehensive_summary(final_metrics: dict,
                              final_region_metrics: dict):
    """输出综合审计结论 (对标 37_dict_coverage_audit log_summary 风格)。

    Args:
        final_metrics:       最终阶段的媒体指标。
        final_region_metrics: 最终阶段的地域指标。
    """
    logger.info("")
    logger.info("=" * 70)
    logger.info("  综合审计结论")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  以下是本次媒体多样性审计的核心指标汇总:")
    logger.info("")

    n_media = final_metrics.get("唯一媒体数", 0)
    hhi = final_metrics.get("HHI", 0)
    enm = final_metrics.get("等效媒体数ENM", 0)
    evenness = final_metrics.get("Pielou均匀度", 0)
    gini = final_metrics.get("Gini系数", 0)
    rated_pct = final_metrics.get("已评级报道占比(%)", 0)
    n_region = final_region_metrics.get("唯一地域数", 0)
    region_hhi = final_region_metrics.get("地域HHI", 0)
    region_evenness = final_region_metrics.get("地域Pielou均匀度", 0)
    coverage = final_region_metrics.get("省份覆盖率", 0)

    logger.info(f"    · 最终唯一媒体数:       {n_media}")
    logger.info(f"    · HHI:                  {hhi:.6f}      "
                 f"({'✓ <0.10 分散' if hhi < 0.10 else '≥0.10 集中'})")
    logger.info(f"    · 等效媒体数 ENM:       {enm:.0f}          "
                 f"[Laakso1979]")
    # fix(omni-g-val-robust-05, 2026-06-11): J' 在 S=1 时为 NaN (不适用),
    # 显示 n/a 而非误导性的数值/阈值判定; 单一媒体垄断由 HHI≥0.10 门捕获。
    if pd.isna(evenness):
        logger.info("    · Pielou 均匀度 J':     n/a       (S=1 单一媒体, J' 不适用)")
    else:
        logger.info(f"    · Pielou 均匀度 J':     {evenness:.4f}    "
                     f"({'✓ ≥0.70' if evenness >= 0.70 else '<0.70'})")
    logger.info(f"    · Gini 系数:            {gini:.4f}    "
                 f"({'✓ <0.80' if gini < 0.80 else '≥0.80 高度不均'})")
    logger.info(f"    · Tier 1-5 报道占比:    {rated_pct:.1f}%    "
                 f"({'✓ ≥40%' if rated_pct >= 40 else '<40%'})")
    logger.info(f"    · 唯一地域数:           {n_region}")
    logger.info(f"    · 地域 HHI:             {region_hhi:.6f}")
    logger.info(f"    · 地域均匀度:           {region_evenness:.4f}")
    logger.info(f"    · 省份覆盖率:           {coverage:.1%}    "
                 f"({'✓ ≥80%' if coverage >= 0.80 else '<80%'})")

    # 自动化判定
    issues = []
    if hhi >= 0.10:
        issues.append(f"媒体 HHI={hhi:.4f} ≥0.10: 来源过度集中于少数媒体")
    # fix(omni-g-val-robust-05, 2026-06-11): NaN (S=1 不适用) 不触发均匀度判定
    if not pd.isna(evenness) and evenness < 0.70:
        issues.append(f"Pielou J'={evenness:.3f} <0.70: 报道数在各媒体间分布不均")
    if gini >= 0.80:
        issues.append(f"Gini={gini:.3f} ≥0.80: 媒体报道数高度不等")
    if rated_pct < 40:
        issues.append(f"已评级报道占比={rated_pct:.1f}% <40%: 大量报道来自未评级媒体")
    if coverage < 0.80:
        issues.append(f"省份覆盖率={coverage:.1%} <80%: 地域覆盖存在盲区")
    if region_hhi >= 0.15:
        issues.append(f"地域HHI={region_hhi:.4f} ≥0.15: 地域分布过度集中")

    logger.info("")
    if issues:
        logger.info(f"  发现 {len(issues)} 项关注事项:")
        for i, issue in enumerate(issues, 1):
            logger.info(f"    {i}. {issue}")
    else:
        logger.info("  ✓ 所有指标均在健康范围内, 媒体多样性表现良好。")

    logger.info("")
    logger.info("  参考文献:")
    for key, ref in REFERENCES.items():
        logger.info(f"    [{key}] {ref}")


# ============================================================================
# 11. 数据加载
# ============================================================================

def load_stage_data(filename_key: str, default_name: str,
                    stage_label: str) -> pd.DataFrame | None:
    """安全加载指定阶段的 parquet 数据。

    Args:
        filename_key: config.filenames 中的键名。
        default_name: 默认文件名。
        stage_label:  日志中的阶段标签。

    Returns:
        pd.DataFrame | None: 加载成功返回 DataFrame，失败返回 None。
    """
    fname = FILENAMES.get(filename_key, default_name)
    fpath = os.path.join(OUTPUT_DIR, fname)
    if not os.path.exists(fpath):
        logger.warning(f"  文件不存在，跳过 {stage_label}: {fpath}")
        return None
    df = pd.read_parquet(fpath)
    logger.info(f"  已加载 {stage_label}: {len(df):,} 行 ({fpath})")
    return df


# ============================================================================
# 12. Excel 导出
# ============================================================================

def export_to_excel(all_results: dict, output_path: str):
    """将所有分析结果导出到多 Sheet 的 Excel 文件。

    Args:
        all_results: 包含各类 DataFrame 的结果字典。
        output_path: 输出 Excel 文件路径。
    """
    if not all_results:
        logger.warning("  无任何分析结果，跳过 Excel 导出")
        return

    logger.info("=" * 60)
    logger.info("导出 Excel 报告")
    logger.info("=" * 60)

    sheet_map = [
        ("overview_df",     "跨阶段总览"),
        ("all_media_df",    "全部媒体"),
        ("top20_df",        "媒体名称_Top20"),
        ("tier_df",         "媒体层级分布"),
        ("tail_df",         "长尾分析"),
        ("region_df",       "地域分布"),
        ("city_df",         "城市分布"),
        ("bank_media_df",   "银行媒体覆盖"),
        ("uncovered_df",    "未覆盖省份"),
        ("temporal_df",     "时序稳定性"),
        ("weight_diag_df",  "权重覆盖诊断"),
        ("delta_df",        "跨阶段差异"),
    ]

    try:
        sheets_written = 0
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for key, sheet_name in sheet_map:
                if key in all_results and not all_results[key].empty:
                    all_results[key].to_excel(
                        writer, sheet_name=sheet_name, index=False)
                    logger.info(f"  Sheet '{sheet_name}': "
                                 f"{len(all_results[key])} 行")
                    sheets_written += 1

            if sheets_written == 0:
                # 填充一个空数据说明 Sheet, 避免 openpyxl IndexError
                pd.DataFrame([{"说明": "本次审计无有效分析结果"}]).to_excel(
                    writer, sheet_name="说明", index=False)
                logger.warning("  所有分析结果为空，已创建占位 Sheet")

        logger.info(f"  Excel 报告已保存: {output_path}")

    except PermissionError:
        logger.error(f"  无法写入 Excel 文件 (可能正被其他程序占用): {output_path}")
    except Exception as e:
        logger.error(f"  Excel 导出失败: {e}", exc_info=True)


# ============================================================================
# 13. 主流程
# ============================================================================

def main():
    """Stage 38 媒体名称与地域多样性审计主流程 (Plan-r3 P3-16 docstring 补齐)。

    8 维度全自动化多样性诊断 — 把 stage 11/12 经过分类筛选后保留的媒体
    -地域分布做完整刻画, 用于论文 "数据来源" 章节的客观性辩护.

    8 维度:
        1. 媒体数量 (Pielou 1966 evenness)
        2. 媒体类型分布 (财经/综合/央媒/地方/网媒)
        3. 媒体地域分布 (省级 / 市级 / 国家级)
        4. Shannon 熵 (1948) — 信息论多样性
        5. Herfindahl 指数 (1950) — 集中度反向
        6. Gini 系数 (1912) — 不平等度
        7. Bushee et al. (2010, JAR) media breadth
        8. Laakso 1979 effective N media

    输入: 跨 6 阶段遍历 (00_preprocessing / 11_bank_news / 12_fintech_news /
          21_tone_llms / 23_bert_tone / 40_article_bank_level 的 parquet)
    输出: ``data/processed/eval_reports/38_media_diversity.xlsx``
    """
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===  38_media_diversity: 媒体名称与地域多样性审计  ===")
    logger.info("=" * 70)
    logger.info("")
    logger.info("  审计框架: 8 维度全自动化多样性诊断")
    logger.info("  学术依据: Shannon (1948), Herfindahl (1950), Pielou (1966),")
    logger.info("            Gini (1912), Bushee et al. (2010), Laakso (1979)")

    # --- 【功能】banner (golden 范式: 让 <stage>.log 自带说明书) ---
    logger.info("=" * 72)
    logger.info("阶段 38: 媒体名称与地域多样性审计 (经典集中度/多样性指标族)")
    logger.info("=" * 72)
    logger.info("【功能】查新闻来源的'家底': 逐道流水线筛子 (00→11→12→21→23→40) 量化")
    logger.info("        '媒体来源'与'地域覆盖'的多样性, 回答审稿人'你的新闻是不是都来自")
    logger.info("        一两家媒体/一两个省', 为论文'数据来源客观性/样本代表性'辩护。")
    logger.info("        产出 = 12-Sheet Excel 体检报告 (不改任何面板数字, 纯诊断终点)。")
    logger.info("【方法】媒体/地域名称多样性: HHI=Σ份额² (Herfindahl) / 等效数 ENM=1/HHI")
    logger.info("        (Laakso-Taagepera) / Shannon 熵 H=-Σpᵢlog₂pᵢ / Pielou 均匀度")
    logger.info("        J'=H/log₂(N) (S=1 单一媒体报 NaN) / Gini 系数 / 加权 HHI (按权威权重)")
    logger.info("        / CRk 集中率; 时序看年际 Jaccard=|交|/|并|; 跨阶段看 HHI 变化率与存留率。")
    logger.info("【判读】HHI/Gini 越低越好 (来源越分散); ENM 越大越好 (相当于几家媒体在干活);")
    logger.info("        J'/Shannon 越高越好 (报道量摊得越匀); 省份覆盖率/Jaccard 越高越好。")
    logger.info("        告警阈值: 媒体 HHI≥0.10 / J'<0.70 / Gini≥0.80 / 已评级报道<40% /")
    logger.info("        省份覆盖<80% / 地域 HHI≥0.15 任一触发即提示来源/地域过度集中。")
    logger.info("【确定性】纯 CPU (pandas/numpy/openpyxl), 无 LLM/Embedding API, $0; 逐位可复现。")

    # --- 加载媒体权重 ---
    media_weights = load_media_weights()
    default_weight = media_weights.get("default", 10)

    # --- 定义待分析阶段 ---
    stages = [
        ("output_00_preprocessing", "00_preprocessing.parquet",
         "00_preprocessing (预处理后)"),
        ("output_11_bank_news", "11_bank_news.parquet",
         "11_bank_news (银行新闻)"),
        # 注 (2026-06-15): 这是 stage 12b 邻近共现硬过滤【之前】的关键词金科阶段
        #   视图 (pre-12b); 媒体多样性审计逐阶段看分布, 此处刻意为原始关键词口径,
        #   非 12b 过滤后的分析宇宙 (后者经 stage 13 → 21 链)。
        ("output_12_fintech_news", "12_fintech_news.parquet",
         "12_fintech_news (金融科技新闻, pre-12b 关键词口径)"),
        ("output_21_tone_llms", "21_tone_llms.parquet",
         "21_tone_llms (LLM验证后)"),
        ("output_23_bert_tone", "23_bert_tone.parquet",
         "23_bert_tone (最终文章级)"),
        ("output_40_article_bank", "40_article_bank_level.parquet",
         "40_article_bank (文章-银行级)"),
    ]

    # --- 收集结果 ---
    overview_rows = []
    all_media_list = []
    all_top20 = []
    all_tier = []
    all_tail = []
    all_region = []
    all_city = []
    all_uncovered = []
    all_temporal = []
    all_weight_diag = []
    bank_media_df = pd.DataFrame()
    stage_media_sets = {}
    last_metrics = {}
    last_region_metrics = {}

    for filename_key, default_name, stage_label in stages:
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"  阶段: {stage_label}")
        logger.info("=" * 60)

        df = load_stage_data(filename_key, default_name, stage_label)
        if df is None:
            continue

        logger.info(f"  总记录数: {len(df):,}")

        # --- A. 媒体名称分析 ---
        logger.info(f"  [A] 媒体名称多样性")
        name_result = analyze_media_names(
            df, stage_label, media_weights, default_weight)

        # 收集媒体名称集合 (用于跨阶段差异)
        media_col = '媒体(中文)'
        if media_col in df.columns:
            stage_media_sets[stage_label] = set(
                df[media_col].fillna("未知").astype(str).unique())

        # --- B. 地域分析 ---
        logger.info(f"  [B] 媒体地域多样性")
        region_result = analyze_regions(df, stage_label)

        # --- C. 时序稳定性分析 ---
        logger.info(f"  [C] 媒体时序稳定性")
        temporal_df = analyze_temporal_stability(
            df, stage_label, media_weights, default_weight)
        if not temporal_df.empty:
            all_temporal.append(temporal_df)

        # --- 汇总跨阶段总览行 ---
        row = {"阶段": stage_label, "总行数": len(df)}
        if "metrics" in name_result:
            row.update(name_result["metrics"])
            last_metrics = name_result["metrics"]
        if "region_metrics" in region_result:
            row.update(region_result["region_metrics"])
            last_region_metrics = region_result["region_metrics"]
        if "n_cities" in region_result:
            row["唯一城市数"] = region_result["n_cities"]
        overview_rows.append(row)

        # --- 累积各类结果 ---
        if "all_media_df" in name_result:
            all_media_list.append(name_result["all_media_df"])
        if "top20_df" in name_result:
            all_top20.append(name_result["top20_df"])
        if "tier_df" in name_result:
            all_tier.append(name_result["tier_df"])
        if "tail_df" in name_result:
            all_tail.append(name_result["tail_df"])
        if "region_df" in region_result:
            all_region.append(region_result["region_df"])
        if "city_df" in region_result:
            all_city.append(region_result["city_df"])
        if "uncovered_df" in region_result and not region_result["uncovered_df"].empty:
            all_uncovered.append(region_result["uncovered_df"])

        # --- D. 最终阶段：按银行分析 ---
        if 'target_bank' in df.columns and stage_label.startswith("40_"):
            logger.info(f"  [D] 按银行的媒体多样性")
            bank_media_df = analyze_bank_media(
                df, media_weights, default_weight)

        # --- E. 权重覆盖诊断 (仅对最终阶段) ---
        if stage_label.startswith("40_") and media_col in df.columns:
            logger.info(f"  [E] 媒体权重覆盖率诊断")
            media_counts = df[media_col].fillna("未知").astype(str).value_counts()
            weight_diag = analyze_weight_coverage(
                media_counts, stage_label, media_weights, default_weight)
            if not weight_diag.empty:
                all_weight_diag.append(weight_diag)

        del df  # 释放内存

    # --- F. 跨阶段差异分析 ---
    delta_df = compute_cross_stage_delta(overview_rows, stage_media_sets)

    # --- 组装 Excel 输出数据 ---
    all_results = {}

    overview_df = pd.DataFrame(overview_rows)
    if not overview_df.empty:
        all_results["overview_df"] = overview_df

    if all_media_list:
        all_results["all_media_df"] = pd.concat(all_media_list, ignore_index=True)
    if all_top20:
        all_results["top20_df"] = pd.concat(all_top20, ignore_index=True)
    if all_tier:
        all_results["tier_df"] = pd.concat(all_tier, ignore_index=True)
    if all_tail:
        all_results["tail_df"] = pd.concat(all_tail, ignore_index=True)
    if all_region:
        all_results["region_df"] = pd.concat(all_region, ignore_index=True)
    if all_city:
        all_results["city_df"] = pd.concat(all_city, ignore_index=True)
    if not bank_media_df.empty:
        all_results["bank_media_df"] = bank_media_df
    if all_uncovered:
        all_results["uncovered_df"] = pd.concat(all_uncovered, ignore_index=True)
    if all_temporal:
        all_results["temporal_df"] = pd.concat(all_temporal, ignore_index=True)
    if all_weight_diag:
        all_results["weight_diag_df"] = pd.concat(all_weight_diag, ignore_index=True)
    if not delta_df.empty:
        all_results["delta_df"] = delta_df

    # --- 打印跨阶段总览 ---
    logger.info("")
    logger.info("=" * 70)
    logger.info("  跨阶段媒体多样性比较摘要")
    logger.info("=" * 70)
    if not overview_df.empty:
        for _, row in overview_df.iterrows():
            stage = row.get("阶段", "?")
            total = row.get("总行数", 0)
            n_media = row.get("唯一媒体数", "-")
            hhi = row.get("HHI", "-")
            top5 = row.get("Top5占比", "-")
            evn = row.get("Pielou均匀度", "-")
            n_region = row.get("唯一地域数", "-")
            rhhi = row.get("地域HHI", "-")

            hhi_str = f"{hhi:.6f}" if isinstance(hhi, float) else str(hhi)
            top5_str = f"{top5:.2%}" if isinstance(top5, float) else str(top5)
            evn_str = f"{evn:.3f}" if isinstance(evn, float) else str(evn)
            rhhi_str = f"{rhhi:.6f}" if isinstance(rhhi, float) else str(rhhi)

            logger.info(
                f"  {stage:<35s} | {total:>8,} 行 | "
                f"媒体={n_media} | HHI={hhi_str} | "
                f"J'={evn_str} | Top5={top5_str} | "
                f"地域={n_region} | 地域HHI={rhhi_str}"
            )

    # --- 综合诊断结论 ---
    if last_metrics and last_region_metrics:
        log_comprehensive_summary(last_metrics, last_region_metrics)

    # --- 【结果分析】banner (golden 范式: 对产出指标逐个判读 + 小样本/降级告警) ---
    logger.info("-" * 72)
    logger.info("【结果分析】媒体多样性审计核心产出逐项判读 (对照阈值给好/坏/临界):")
    n_stages_done = len(overview_rows)
    logger.info(f"  · 成功分析阶段数: {n_stages_done}/6 "
                f"({'✓ 全部 6 阶段就绪' if n_stages_done >= 6 else '部分阶段 parquet 缺失, 见上方 WARNING'})")

    if last_metrics:
        fin_media = last_metrics.get("唯一媒体数", 0)
        fin_hhi = last_metrics.get("HHI", 0.0)
        fin_enm = last_metrics.get("等效媒体数ENM", 0.0)
        fin_evn = last_metrics.get("Pielou均匀度", float('nan'))
        fin_gini = last_metrics.get("Gini系数", 0.0)
        fin_rated = last_metrics.get("已评级报道占比(%)", 0.0)
        hhi_verdict = ("✓ <0.10 来源分散 (好)" if fin_hhi < 0.10
                       else "⚠ ≥0.10 来源向少数媒体集中 (坏)")
        gini_verdict = "✓ <0.80 (好)" if fin_gini < 0.80 else "⚠ ≥0.80 报道数高度不等 (坏)"
        rated_verdict = "✓ ≥40% (好)" if fin_rated >= 40 else "⚠ <40% 大量未评级媒体 (坏)"
        logger.info(f"  · 最终阶段(40_article_bank)唯一媒体数: {fin_media} 家, "
                    f"等效媒体数 ENM={fin_enm:.0f} (越大越好, 相当于几家媒体在均匀供稿)")
        logger.info(f"  · 媒体 HHI={fin_hhi:.6f} → {hhi_verdict}")
        if pd.isna(fin_evn):
            logger.info("  · Pielou 均匀度 J': n/a (S=1 单一媒体垄断, J' 不适用; 集中度已由 HHI 门捕获)")
        else:
            evn_verdict = "✓ ≥0.70 报道摊得匀 (好)" if fin_evn >= 0.70 else "⚠ <0.70 报道分布不均 (坏)"
            logger.info(f"  · Pielou 均匀度 J'={fin_evn:.4f} → {evn_verdict}")
        logger.info(f"  · Gini 系数={fin_gini:.4f} → {gini_verdict}")
        logger.info(f"  · Tier1-5 已评级报道占比={fin_rated:.1f}% → {rated_verdict}")

    if last_region_metrics:
        reg_n = last_region_metrics.get("唯一地域数", 0)
        reg_hhi = last_region_metrics.get("地域HHI", 0.0)
        reg_cov = last_region_metrics.get("省份覆盖率", 0.0)
        reg_hhi_verdict = ("✓ <0.15 地域分散 (好)" if reg_hhi < 0.15
                           else "⚠ ≥0.15 地域过度集中 (坏)")
        cov_verdict = "✓ ≥80% (好)" if reg_cov >= 0.80 else "⚠ <80% 地域覆盖存盲区 (坏)"
        logger.info(f"  · 最终阶段唯一地域数: {reg_n} 个 | 地域 HHI={reg_hhi:.6f} → {reg_hhi_verdict}")
        logger.info(f"  · 省份覆盖率={reg_cov:.1%} → {cov_verdict}")

    # 时序稳定性 (年际 Jaccard 平均, ≥0.7 视为媒体构成跨年稳定)
    if all_temporal:
        try:
            temporal_all = pd.concat(all_temporal, ignore_index=True)
            jac_vals = temporal_all['Jaccard相似度'].dropna()
            jac_vals = jac_vals[jac_vals > 0]
            if len(jac_vals) > 0:
                avg_jac = float(jac_vals.mean())
                jac_verdict = ("✓ ≥0.70 媒体构成跨年稳定 (好)" if avg_jac >= 0.70
                               else "ℹ 0.50-0.70 有一定变动" if avg_jac >= 0.50
                               else "⚠ <0.50 媒体构成跨年变动大 (坏)")
                logger.info(f"  · 年际媒体 Jaccard 相似度均值={avg_jac:.3f} → {jac_verdict}")
        except Exception:  # noqa: BLE001 — 仅日志统计, 失败不影响产物
            logger.info("  · 年际 Jaccard 统计跳过 (时序数据不足或列缺失)")
    else:
        logger.info("  · 时序稳定性: 无可用年份数据 (各阶段年份<2, 已跳过 Jaccard)")

    # 跨阶段存留率 (流水线每过一道筛子媒体多样性损耗)
    if not delta_df.empty and '媒体存留率' in delta_df.columns:
        min_ret = float(delta_df['媒体存留率'].min())
        max_hhi_jump = float(delta_df['HHI变化率(%)'].abs().max())
        logger.info(f"  · 跨阶段最低媒体存留率={min_ret:.1%} "
                    f"({'✓ 各筛子保留多数来源' if min_ret >= 0.50 else '⚠ 某筛子大幅削减来源, 见跨阶段差异 Sheet'})")
        logger.info(f"  · 跨阶段最大 HHI 变化率={max_hhi_jump:.1f}% "
                    f"({'某筛子显著改变集中度, 需复核是否过度过滤' if max_hhi_jump > 20 else '集中度跨筛子平稳'})")

    # 按银行覆盖 (仅 40_ 阶段产出)
    if not bank_media_df.empty:
        mean_breadth = float(bank_media_df['唯一媒体数'].mean())
        logger.info(f"  · 按银行媒体广度 (Bushee2010 breadth): "
                    f"{len(bank_media_df)} 家银行, 平均唯一媒体数={mean_breadth:.1f} 家/行")

    # 小样本 / 优雅降级告警
    n_stage40 = sum(1 for r in overview_rows
                    if str(r.get("阶段", "")).startswith("40_"))
    if n_stage40 == 0:
        logger.warning("  ⚠ 未分析到 40_article_bank 阶段 (parquet 缺失): "
                       "按银行覆盖/权重诊断/最终综合结论将基于上游阶段, 代表性下降。")
    logger.info("  ⚠ 小样本提示: 本机盘面为 T=2 (2017-2018) 子样, 上述多样性结论仅验证")
    logger.info("    审计管道正确性; 全量结论以 17M 文章 / T=18 (2007-2024) 实测为准。")
    logger.info("-" * 72)

    # --- 导出 Excel ---
    output_path = os.path.join(EVAL_DIR, "38_media_diversity.xlsx")
    export_to_excel(all_results, output_path)

    # --- 阶段摘要 ---
    final_media = overview_rows[-1].get("唯一媒体数", 0) if overview_rows else 0
    final_region = overview_rows[-1].get("唯一地域数", 0) if overview_rows else 0
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=overview_rows[0].get("总行数", 0) if overview_rows else 0,
        output_rows=len(overview_rows),
        extra_info={
            "分析阶段数": len(overview_rows),
            "最终唯一媒体数": final_media,
            "最终唯一地域数": final_region,
            "Excel输出": output_path,
        }
    )

    logger.info(f"38_media_diversity 执行完毕")


if __name__ == '__main__':
    main()
