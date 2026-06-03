"""
41_panel_encode_aggregate.py — 篇章级编码与 Bank-Year 聚合
==========================================================

功能:
  - 共享全局配置 (CONFIG, logger, OUTPUT_DIR 等)
  - 情感数值编码 (encode_sentiment)
  - 媒体权威性加权 (compute_media_authority_weights)
  - 时间解析 (parse_time)
  - 聚合字典构建 (build_aggregation_dict)
  - Bank-Year 聚合 (aggregate_panel)
  - 面板平衡 (balance_panel)

拆分自: 40_build_panel.py
学术依据: Tetlock et al. (2008, JF) 先分后合范式
"""

import json
import os
import re
import sys
import warnings

# Phase 5c-1: 解析 ``news_process.core.*`` 需要项目根 (news_process/ 父目录)
# 在 sys.path 中。包模式 / pytest fixture / 根 shim 调用都安全。
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 1. 全局配置与初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "40_build_panel"  # 保留原名, 兼容日志文件命名约定
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 输出路径
OUTPUT_DIR = CONFIG["paths"]["output_dir"]
FILENAMES = CONFIG.get("filenames", {})
PANEL_CFG = CONFIG.get("panel_building", {})

# LLM 模型 short_name 列表(从 tone_llm_processing.models 读取)
# 这些名称用于定位阶段 21 输出中各模型对应的情感结果列
# v3 锁定: gpt54nano (OpenAI) / gemini31111 (Google) / deepseekv4 (DeepSeek)
_llm_cfg = CONFIG.get('tone_llm_processing', {}).get('models', [])
LLM_MODELS = [m['short_name'] for m in _llm_cfg] if _llm_cfg else ['gpt54nano', 'gemini31111', 'deepseekv4']

# 词典名列表 — 对应阶段 22 中的五本中文金融情感词典
DICT_NAMES = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

# BERT 模型 short_name 列表与分类数（从 sentiment_analysis.tone_berts.models 读取）
_bert_cfg = CONFIG.get('sentiment_analysis', {}).get('tone_berts', {}).get('models', [])
BERT_MODELS = [m['short_name'] for m in _bert_cfg] if _bert_cfg else ['finbert_cn', 'fin_sent_zh', 'finbert2']

# 三分类模型（有 _中性 列）
THREE_CLASS_MODELS = set()
for m in _bert_cfg:
    lm = m.get('label_map', {})
    if '中性' in lm.values():
        THREE_CLASS_MODELS.add(m['short_name'])
if not THREE_CLASS_MODELS:
    THREE_CLASS_MODELS = {'finbert_cn', 'fin_sent_zh'}


# ============================================================================
# 2. 情感编码函数
# 将三分类中文标签映射为数值, 便于 Stata 回归使用:
#   正面 -> +1, 中性 -> 0, 负面 -> -1
# ============================================================================

SENTIMENT_MAP = {'正面': 1, '中性': 0, '负面': -1}


def encode_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """篇章级情感数值编码：离散 + 连续（双轨）。

    v6/F2 改动 (篇章级编码契约重写)
    --------------------------------
    历史：`llm_sentiment{track}.map(SENTIMENT_MAP).fillna(0)` 把所有缺失值
          (verification 失败 / tie undefined / API 调用失败 / 真实中性)
          统一坍塌为 0，导致 is_neutral 列同时混入 4 类语义不可分。

    v6 行为：
      1. 使用 nullable Int8 (pd.Int8 / pd.NA) 保留 NaN 语义；
      2. 显式合并 4 个掩码列：llm_call_failure / llm_undefined / llm_verified=False
         → 这三类的 vote_score 强制为 NaN，与"真实中性"严格区分；
      3. is_positive/is_negative/is_neutral 三列均改为 nullable Int8；
         `is_neutral{track}` 仅在 verified=True ∧ undefined=0 ∧ failure=0 ∧
         sentiment="中性" 时为 1，否则 NaN；
      4. 下游 sum 自动跳过 NaN，count() 给出"有效观测数"。
    """
    logger.info("=" * 60)
    logger.info("步骤 2: 篇章级情感数值编码（双轨, v6/F2 nullable Int8 版本）")
    logger.info("=" * 60)

    encoded_cols = []
    for track in ['_full', '_ctx']:
        # remove-title-track: 标题情感轨已永久停产, 仅遍历 _full / _ctx 双轨;
        # 此守卫只防上游 stage 21 未产出对应轨道列 (llm_sentiment{track}) 时优雅跳过。
        if f'llm_sentiment{track}' not in df.columns:
            logger.info(f"  跳过 {track} 轨道编码（列 llm_sentiment{track} 不存在）")
            continue

        # ── v6/F2: 准备掩码 ──
        sent_col = f'llm_sentiment{track}'
        ver_col = f'llm_verified{track}'
        # _full / _ctx 双轨均含 verification 步骤 (标题情感轨已停产)
        has_verification = ver_col in df.columns

        # 测量失败掩码（call_failure / undefined）：仅 _full / _ctx 有
        cf_col = f'llm_call_failure{track}'
        ud_col = f'llm_undefined{track}'
        invalid_mask = pd.Series(False, index=df.index)
        if cf_col in df.columns:
            invalid_mask = invalid_mask | df[cf_col].fillna(0).astype(bool)
        if ud_col in df.columns:
            invalid_mask = invalid_mask | df[ud_col].fillna(0).astype(bool)

        # verified=False 也视为情感不可信（v6/F2: 不再坍塌为"中性"）
        if has_verification:
            ver_invalid = ~df[ver_col].fillna(False).astype(bool)
            invalid_mask = invalid_mask | ver_invalid

        # ── 离散 vote_score: nullable Int8，无效行 → <NA> ──
        raw_score = df[sent_col].map(SENTIMENT_MAP)
        # 把 sentiment 是 None / NaN 的也视为无效
        raw_score = raw_score.where(~df[sent_col].isna(), other=pd.NA)
        raw_score = raw_score.where(~invalid_mask, other=pd.NA)
        df[f'llm_vote_score{track}'] = raw_score.astype('Int8')

        # ── 三个二值掩码（nullable Int8，无效行 → <NA>）──
        df[f'is_positive{track}'] = (df[f'llm_vote_score{track}'] == 1).astype('Int8')
        df[f'is_negative{track}'] = (df[f'llm_vote_score{track}'] == -1).astype('Int8')
        df[f'is_neutral{track}'] = (df[f'llm_vote_score{track}'] == 0).astype('Int8')
        # 把无效行的三列从 0 强制设回 <NA>（pandas 比较运算符在 <NA> 上返回 False）
        for c in [f'is_positive{track}', f'is_negative{track}', f'is_neutral{track}']:
            df.loc[invalid_mask, c] = pd.NA
            df.loc[df[sent_col].isna(), c] = pd.NA

        # ── 连续编码 (Float32, NaN 语义) ──
        ar_col = f'llm_agreement_rate{track}'
        ar_v = df[ar_col].astype('Float32') if ar_col in df.columns else pd.Series(1.0, index=df.index, dtype='Float32')
        # vote_cont = score × agree_rate (自然传播 NaN)
        df[f'llm_vote_cont{track}'] = df[f'llm_vote_score{track}'].astype('Float32') * ar_v

        # ── LLM 逐模型 离散 + 连续 ──
        for short in LLM_MODELS:
            m_sent = f'{short}_sentiment{track}'
            m_conf = f'{short}_sentiment_confidence{track}'
            m_ver = f'{short}_verified{track}'
            if m_sent in df.columns:
                m_score = df[m_sent].map(SENTIMENT_MAP)
                m_score = m_score.where(~df[m_sent].isna(), other=pd.NA)
                # 单模型 verified=False 时该模型自身的 score 也置 NA
                if m_ver in df.columns:
                    m_inv = ~df[m_ver].fillna(False).astype(bool)
                    m_score = m_score.where(~m_inv, other=pd.NA)
                df[f'{short}_score{track}'] = m_score.astype('Int8')

                if m_conf in df.columns:
                    df[f'{short}_cont{track}'] = (
                        df[f'{short}_score{track}'].astype('Float32')
                        * df[m_conf].astype('Float32')
                    )
                else:
                    df[f'{short}_cont{track}'] = df[f'{short}_score{track}'].astype('Float32')

        encoded_cols.extend([
            f'llm_vote_score{track}', f'is_positive{track}', f'is_negative{track}',
            f'is_neutral{track}', f'llm_vote_cont{track}'
        ])
        for short in LLM_MODELS:
            encoded_cols.extend([f'{short}_score{track}', f'{short}_cont{track}'])

    # --- 词典法 & BERT: 直接使用上游连续值, 无需额外编码 ---

    # --- LLM 置信度合成列 (Shapiro, Sudhof & Wilson 2022, JoE;
    #     Baker et al. 2024, JAR — 信号清晰度/衰减偏误调节) ---
    # 三模型情感置信度的宏平均, 用于下游面板聚合
    # 学术依据:
    #   Shapiro, A.H., Sudhof, M. & Wilson, D.J. (2022).
    #   'Measuring News Sentiment.'
    #   Journal of Econometrics, 228(2), 221-243.
    #   DOI: 10.1016/j.jeconom.2020.07.053
    #   → 情感度量噪声导致回归系数衰减偏误(attenuation bias)
    #   → LLM 置信度低 = 信号噪声大 → 情感效应被低估
    for track in ['_full', '_ctx']:
        conf_cols = [f'{s}_sentiment_confidence{track}' for s in LLM_MODELS
                     if f'{s}_sentiment_confidence{track}' in df.columns]
        if conf_cols:
            df[f'avg_llm_conf{track}'] = df[conf_cols].mean(axis=1)
            logger.info(f"  avg_llm_conf{track}: 由 {len(conf_cols)} 个模型置信度合成")
        else:
            logger.warning(f"  未找到 LLM 置信度列, 跳过 avg_llm_conf{track}")

    logger.info(f"  生成编码列: {len(encoded_cols)} 个")
    logger.info(f"  离散映射: 正面=1, 中性=0, 负面=-1")
    logger.info(f"  连续编码: direction × confidence ∈ [-1, +1]")

    # Logit-to-Score 概率分数诊断（如果 21_tone_llms 已生成）
    for track in ['_full', '_ctx']:
        src = f'llm_prob_score{track}'
        if src in df.columns:
            valid = df[src].notna()
            logger.info(f"  {src}: mean={df.loc[valid, src].mean():.4f}, "
                        f"std={df.loc[valid, src].std():.4f}, n={valid.sum()}")

    return df


# explode_banks 函数已移除 — 展开逻辑已迁移至 11_news_bank.py（Phase 1 提早展开）
# 数据抵达此阶段时已包含 target_bank、co_mentioned_banks 等列

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

    df = df.copy()

    if df.empty:
        logger.info("  数据框为空, 跳过媒体权威性加权")
        df['media_authority_weight'] = 1.0
        return df

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
# 3c.bis 媒体声誉 3 级分类权重 (v3.6.1 PR #6, C1)
# ============================================================================
# 与 compute_media_authority_weights 并行存在 (不覆盖原列), 仅作 robustness:
#   - main spec 仍用 'media_authority_weight' (raw_series / raw_mean, continuous)
#   - 'media_authority_weight_tier' 新列作 paper Table A8 sensitivity
# 学术依据:
#   Solomon (2012). The Review of Financial Studies, 25(8), 3306-3322.
#     → IR 选择高 prestige 媒体投放; outlet effect 显著
#   Engelberg & Parsons (2011). Journal of Finance, 66(1), 67-97.
#     → 局部报纸覆盖的因果识别 (地理 IV)
#   Hillert, Jacobs & Müller (2014). Journal of Finance, 69(5), 2095-2143.
# 数据源:
#   config/media_classification.json (3 级名录, central 171 / financial 15 /
#   comprehensive 27).
# 设计:
#   tier 权重组合 (2.5, 2.0, 1.5) baseline + (3, 2, 1.5) high spread +
#   (1, 1, 1) ablation 三组 sensitivity. main 仍走 continuous, 不破坏
#   9 paper 已发布 SSRN 草稿契约.

_TIER_WEIGHTS_DEFAULT = {
    'central': 2.5,
    'financial': 2.0,
    'comprehensive': 1.5,
    'other': 1.0,
}


def compute_media_tier_weights(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """v3.6.1 C1: 基于 media_classification.json 3 级分类的离散权重.

    与 compute_media_authority_weights 并行 (不覆盖). 输出列:
        'media_authority_weight_tier'  (paper Table A8 sensitivity 用)
        'media_tier_label'             ('central'/'financial'/'comprehensive'/'other')

    Args:
        df: 必含 '媒体(中文)' 列.
        weights: 4 类 tier → 权重 dict; ``None`` 用 _TIER_WEIGHTS_DEFAULT.

    Returns:
        附加 2 列的 DataFrame.

    Note:
        若 config/media_classification.json 不存在或解析失败, 全部归 'other'
        权重 1.0 (退化为 ablation case, 不破坏下游).
    """
    logger.info("=" * 60)
    logger.info("步骤 3c.bis: 媒体声誉 3 级 tier 权重 (v3.6.1 C1)")
    logger.info("=" * 60)

    weights = weights or _TIER_WEIGHTS_DEFAULT
    df = df.copy()

    if df.empty or '媒体(中文)' not in df.columns:
        df['media_authority_weight_tier'] = 1.0
        df['media_tier_label'] = 'other'
        return df

    cls_path = CONFIG['paths'].get(
        'media_classification_file',
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), 'config', 'media_classification.json'),
    )
    if not os.path.exists(cls_path):
        logger.warning(f"  media_classification.json 不存在: {cls_path}; "
                       f"全 'other' 权重 1.0 (ablation 退化)")
        df['media_authority_weight_tier'] = 1.0
        df['media_tier_label'] = 'other'
        return df

    with open(cls_path, 'r', encoding='utf-8') as f:
        cls = json.load(f)

    central = frozenset(cls.get('central_media', []))
    financial = frozenset(cls.get('financial_media', []))
    comprehensive = frozenset(cls.get('comprehensive_media', []))

    # 3 集互斥假设: financial / comprehensive 优先级 > central (避免人民日报
    # 等同时在 central + comprehensive 的双归属); 由 paper-author 判定的
    # 专业性 > 政治权威性.
    def _classify(name: str) -> str:
        name_str = str(name).strip()
        if name_str in financial:
            return 'financial'
        if name_str in comprehensive:
            return 'comprehensive'
        if name_str in central:
            return 'central'
        # 去括号 fuzzy 匹配 (与 compute_media_authority_weights 对齐)
        norm = re.sub(r'[（(][^)）]*[)）]', '', name_str).strip()
        if norm in financial:
            return 'financial'
        if norm in comprehensive:
            return 'comprehensive'
        if norm in central:
            return 'central'
        return 'other'

    labels = df['媒体(中文)'].apply(_classify)
    df['media_tier_label'] = labels
    df['media_authority_weight_tier'] = labels.map(weights).astype(float)

    # ── 诊断日志 ──
    counts = labels.value_counts()
    total = len(df)
    for tier in ('central', 'financial', 'comprehensive', 'other'):
        n = int(counts.get(tier, 0))
        logger.info(f"  tier={tier:<14} n={n:>7} ({n/total:.1%}) "
                    f"weight={weights[tier]}")
    logger.info(f"  权重列: mean={df['media_authority_weight_tier'].mean():.4f}, "
                f"std={df['media_authority_weight_tier'].std():.4f}")

    return df


# ============================================================================
# 4. 时间解析
# ============================================================================

def parse_time(df: pd.DataFrame) -> pd.DataFrame:
    """从日期列提取年份。"""
    logger.info("=" * 60)
    logger.info("步骤 4: 时间解析")
    logger.info("=" * 60)

    df = df.copy()
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

def build_aggregation_dict(df: pd.DataFrame | None = None) -> dict:
    """构建 GroupBy 聚合字典(双轨)。

    聚合策略遵循 Tetlock et al. (2008, JF) 范式:
      - mean: Bank-Year 均值(核心情感指标)
      - sum:  Bank-Year 总和(加权指标的分子)
      - std:  Bank-Year 标准差(情感分散度, 反映信息环境不确定性)
      - count: 新闻覆盖量

    双轨(_full + _ctx)确保全文和上下文片段两种输入分别聚合,
    供下游消融研究和稳健性检验使用。

    Args:
        df: 可选, 用于 herd_weight 双轨/单轨 schema 检测 (Plan E P1 B3).
            v3.6.0+ 推荐传入; None 时默认假设双轨列存在 (与新 stage 24 一致)。
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

    # --- J. LLM 置信度聚合 (Shapiro, Sudhof & Wilson 2022, JoE;
    #        Baker et al. 2024, JAR — 信号清晰度/衰减偏误调节) ---
    # 学术依据: 情感度量的信噪比直接影响回归系数的估计精度
    # (Shapiro et al. 2022, Section 4: attenuation bias correction)
    # 置信度越低 → 测量误差越大 → Tone 对因变量的估计系数向零衰减
    for track in ['_full', '_ctx']:
        # 三模型宏平均置信度 → Bank-Year 均值 & 标准差
        agg[f'avg_llm_conf{track}'] = (f'avg_llm_conf{track}', 'mean')
        agg[f'avg_llm_conf_std{track}'] = (f'avg_llm_conf{track}', 'std')
        # 逐模型置信度 → Bank-Year 均值 (稳健性分解)
        for short in LLM_MODELS:
            conf_src = f'{short}_sentiment_confidence{track}'
            agg[f'avg_{short}_conf{track}'] = (conf_src, 'mean')

    # --- E. 新闻覆盖量 & 稳健性辅助（无需双轨） ---

    # P1 修复 (metric-audit 2026-06-02, encode-02 正确重构): n_articles = 物理新闻
    # 篇数 (Fang-Peress 2009 JF media coverage, 'size' 计全组行数含 NA), 供
    # ln_news_coverage / falsification 等 coverage 消费者. 分类组成型比率
    # (tech/app/sub/symb/indep/collab_frac) 与其恒等式改用 n_articles_llm_valid
    # (LLM 有效投票篇数 = 分类定义域, 'count' 跳 NA), 保持分子分母同口径、值不变.
    agg['n_articles'] = ('llm_vote_score_full', 'size')
    agg['n_articles_llm_valid'] = ('llm_vote_score_full', 'count')
    # metric-audit 2026-06-02 final: ctx 轨独立有效投票篇数 (= ctx 分类 frac 的正确分母).
    # ctx 对角线分类 frac (tech/app_lc, sub/symb_sc, indep/collab_cm) 分子用 ctx 轨计数
    # (llm_vote_score_ctx 'count'), 但旧实现分母错用 full 轨 n_articles_llm_valid → 轨道
    # 不对称除法 (ctx_valid>full_valid 时 frac 越界至 3.0, ctx_valid<full_valid 时低估).
    # 两轨独立 LLM 成功率不同 (同 c8a70ac5 _ctx 计数 sanity), ctx frac 须用 ctx 分母:
    # 分子(类内 ctx-valid) ≤ 分母(全 ctx-valid) 数学保证 frac∈[0,1], 对子和≤1 (残余=ctx
    # -valid 但无 locus/subst/collab 标签, 正确语义).
    agg['n_articles_llm_valid_ctx'] = ('llm_vote_score_ctx', 'count')
    agg['headline_frac'] = ('in_title', 'mean')
    agg['multi_bank_frac'] = ('is_multi_bank', 'mean')
    agg['avg_bank_count'] = ('bank_count', 'mean')
    agg['max_bank_count'] = ('bank_count', 'max')
    agg['avg_agreement_rate_full'] = ('llm_agreement_rate_full', 'mean')
    agg['avg_agreement_rate_ctx'] = ('llm_agreement_rate_ctx', 'mean')
    # remove-title-track: avg_agreement_rate_title 已取消

    # --- E2. v3.7.2 R8-H1 全管道延伸: ctx 独立度信号 ---
    # ctx_is_fallback (article, bool): True iff content_ctx ≡ content_full (entity-miss)
    # → frac_ctx_fallback (bank-year, mean): 高值=ctx 轨等价于 full 轨, 双轨退化为单轨
    # → n_articles_for_ctx_independence (bank-year, count): 真双轨文章绝对数,
    #    避免按比例 filter 时的银行规模偏差 (大行总通过, 小行总被剔)
    # 论文用途: P1 (llm_vote_tone_ctx) / P11 (mean_clarity_score_ctx) 的 robustness
    # 锚定: lexical_discriminant_validity.py:20 (R8-H1) + Hassan 2019 QJE proximity
    if df is not None and 'ctx_is_fallback' in df.columns:
        agg['frac_ctx_fallback'] = ('ctx_is_fallback', 'mean')
        # n_articles_for_ctx_independence = sum(~ctx_is_fallback)
        # 用 size-then-subtract 而非 lambda 以兼容 pandas groupby.agg 的 NamedAgg 协议
        agg['_ctx_fallback_count'] = ('ctx_is_fallback', 'sum')

    # --- E3. v3.7.4 P3.1.5: title indicators bank-year aggregation ---
    # title_mentions_fintech (article bool) → frac_title_mentions_fintech (bank-year mean)
    # title_length_bucket (article {0,1}) → frac_title_long (bank-year mean of bucket==1)
    # 用途: Panel D/E stratified robustness (v3.7.4 Plan A v1.0)
    # 锚定: Antweiler-Frank (2004) JF subject-relevance threshold;
    #        Da-Engelberg-Gao (2011) JF attention-channel separation
    # remove-title-track: frac_title_mentions_fintech / frac_title_long 已取消

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
    # --- F4. 跟风衰减权重 (Tetlock 2011, JF) — 作为面板控制变量 ---
    # v3.6.0 (Plan E P1 B3): herd_weight 双轨独立 (Edwards 2001 ORM)
    # 兼容: 若仅存在 v3.5.0 legacy herd_weight 单列, 双轨均映射到该列
    # (退化为单轨, 但保持下游引用稳定)
    # df=None 时默认新双轨 schema (v3.6.0+); 否则按列存在性 fallback
    # ⚠ Round 1 M1 修复: legacy fallback (仅 herd_weight 单列) 会让 _hw_full_src
    # 与 _hw_ctx_src 都指向同一列 → panel 出 sum_herd_weight_full == _ctx,
    # 下游误判为真双轨. 这是 silent fake-dual-track 风险, 必须 logger.warning
    # 让用户知道. 真双轨要求重跑 v3.6.0 stage 24.
    if df is not None:
        _has_dual = ('herd_weight_full' in df.columns and
                     'herd_weight_ctx' in df.columns)
        _has_legacy = 'herd_weight' in df.columns
        if _has_dual:
            _hw_full_src = 'herd_weight_full'
            _hw_ctx_src = 'herd_weight_ctx'
        elif _has_legacy:
            _hw_full_src = 'herd_weight'
            _hw_ctx_src = 'herd_weight'  # 显式同源 (fake 双轨)
            logger.warning(
                "build_aggregation_dict 检测到 legacy 'herd_weight' 单列 "
                "(v3.5.x schema), 双轨聚合将退化为单源 — panel 中 "
                "sum_herd_weight_full == sum_herd_weight_ctx (fake 双轨). "
                "如需真双轨, 请重跑 stage 24 (v3.6.0 双轨 herd_decay)."
            )
        else:
            # 无任何 herd 列 — agg dict 仍注册以保持 schema 稳定,
            # valid_agg 过滤后会自动跳过
            _hw_full_src = 'herd_weight_full'
            _hw_ctx_src = 'herd_weight_ctx'
    else:
        _hw_full_src = 'herd_weight_full'
        _hw_ctx_src = 'herd_weight_ctx'
    agg['avg_herd_weight_full'] = (_hw_full_src, 'mean')
    agg['min_herd_weight_full'] = (_hw_full_src, 'min')
    agg['avg_herd_weight_ctx'] = (_hw_ctx_src, 'mean')
    agg['min_herd_weight_ctx'] = (_hw_ctx_src, 'min')
    # --- F5. 跟风衰减加权聚合 (Tetlock 2011, JF) ---
    # 双轨 sum 用于下游 hw_denom 除法 (encode.py:1200-1214)
    agg['sum_herd_weight_full'] = (_hw_full_src, 'sum')
    agg['sum_herd_weight_ctx'] = (_hw_ctx_src, 'sum')
    for track in ['_full', '_ctx']:
        agg[f'llm_vote_score_hw_sum{track}'] = (f'llm_vote_score_hw{track}', 'sum')
        agg[f'llm_vote_cont_hw_sum{track}'] = (f'llm_vote_cont_hw{track}', 'sum')
        for short in LLM_MODELS:
            agg[f'{short}_score_hw_sum{track}'] = (f'{short}_score_hw{track}', 'sum')
            agg[f'{short}_cont_hw_sum{track}'] = (f'{short}_cont_hw{track}', 'sum')
        for d in DICT_NAMES:
            agg[f'{d}_score_hw_sum{track}'] = (f'{d}_score_hw{track}', 'sum')
            agg[f'{d}_idf_score_hw_sum{track}'] = (f'{d}_idf_score_hw{track}', 'sum')
        for b in BERT_MODELS:
            agg[f'{b}_正面_hw_sum{track}'] = (f'{b}_正面_hw{track}', 'sum')
            agg[f'{b}_负面_hw_sum{track}'] = (f'{b}_负面_hw{track}', 'sum')
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

    # --- K. 洗稿率聚合: 多方法 × 双轨 (Bingler et al. 2022, FRL) ---
    for track in ['_full', '_ctx']:
        # A: LLM 投票
        agg[f'pos_symb_count{track}'] = (f'_is_pos_symb{track}', 'sum')
        # B: 反向验证
        agg[f'neg_sub_count{track}'] = (f'_is_neg_sub{track}', 'sum')
        # A2: 单个 LLM (Loughran & McDonald 2016, JAR)
        for llm in LLM_MODELS:
            agg[f'{llm}_pos_count{track}'] = (f'_is_{llm}_positive{track}', 'sum')
            agg[f'{llm}_pos_symb_count{track}'] = (f'_is_{llm}_pos_symb{track}', 'sum')
        # D: 词典均值
        agg[f'dict_pos_count{track}'] = (f'_is_dict_positive{track}', 'sum')
        agg[f'dict_pos_symb_count{track}'] = (f'_is_dict_pos_symb{track}', 'sum')
        # D2: 单个词典 (Gentzkow et al. 2019, JEL)
        for d in DICT_NAMES:
            agg[f'{d}_pos_count{track}'] = (f'_is_{d}_positive{track}', 'sum')
            agg[f'{d}_pos_symb_count{track}'] = (f'_is_{d}_pos_symb{track}', 'sum')
        # E: BERT 均值
        agg[f'bert_pos_count{track}'] = (f'_is_bert_positive{track}', 'sum')
        agg[f'bert_pos_symb_count{track}'] = (f'_is_bert_pos_symb{track}', 'sum')
        # E2: 单个 BERT (Huang et al. 2023, CAR)
        for b in BERT_MODELS:
            agg[f'{b}_pos_count{track}'] = (f'_is_{b}_positive{track}', 'sum')
            agg[f'{b}_pos_symb_count{track}'] = (f'_is_{b}_pos_symb{track}', 'sum')
        # F: 高置信度子样本
        agg[f'pos_hc_count{track}'] = (f'_is_pos_hc{track}', 'sum')
        agg[f'pos_symb_hc_count{track}'] = (f'_is_pos_symb_hc{track}', 'sum')

    # --- L. 单方法 neg_count (用于 disag 指标) ---
    # Garcia, D. (2013). Sentiment during recessions.
    #   The Journal of Finance, 68(3), 1267-1300. DOI: 10.1111/jofi.12027
    #   → 正负面分离避免极性对冲掩蔽, 为下游 disag 公式提供输入
    for track in ['_full', '_ctx']:
        for llm in LLM_MODELS:
            agg[f'{llm}_neg_count{track}'] = (f'_is_{llm}_negative{track}', 'sum')
        for d in DICT_NAMES:
            agg[f'{d}_neg_count{track}'] = (f'_is_{d}_negative{track}', 'sum')
        for b in BERT_MODELS:
            agg[f'{b}_neg_count{track}'] = (f'_is_{b}_negative{track}', 'sum')

    # --- M. 单词典 pos_ratio / neg_ratio 聚合 (词级 disag 输入) ---
    # 姜富伟, 李梦如, 孟令超 (2024). 经济学（季刊）, 24(6), 2281-2300.
    #   DOI: 10.13821/j.cnki.ceq.2024.06.19
    for track in ['_full', '_ctx']:
        for d in DICT_NAMES:
            agg[f'avg_{d}_pos_ratio{track}'] = (f'{d}_pos_ratio{track}', 'mean')
            agg[f'avg_{d}_neg_ratio{track}'] = (f'{d}_neg_ratio{track}', 'mean')

    # --- N. 相对披露密度 (Abraham et al. 2024, JAR, 62(5), 1611-1660) ---
    # DOI: 10.1111/1475-679X.12570
    #   → 篇章级 fintech_word_ratio 在 aggregate_panel() 中预计算,
    #     此处仅注册聚合入口
    agg['avg_ft_word_ratio'] = ('_ft_word_ratio', 'mean')
    agg['avg_ft_word_ratio_std'] = ('_ft_word_ratio', 'std')

    # --- O. 技术重度 (14_fintech_intensity.py, Li et al. 2021, RFS) ---
    # DOI: 10.1093/rfs/hhaa079
    #   → TF-IDF + SIF 质心连续型技术强度得分, Bank-Year 均值聚合
    #   → v3.6.0 (Plan E P4 B1 + D2): 双轨化 — fintech_intensity_score_{full,ctx}
    #     legacy 单列 fintech_intensity_score 由 stage 14 保留为 _full alias
    #   → 防御: 若跳过阶段 14, 任一列不存在, valid_agg 自动跳过, 不引发 KeyError
    agg['avg_ft_intensity'] = ('fintech_intensity_score', 'mean')  # legacy alias
    agg['avg_ft_intensity_std'] = ('fintech_intensity_score', 'std')
    agg['avg_ft_intensity_full'] = ('fintech_intensity_score_full', 'mean')
    agg['avg_ft_intensity_full_std'] = ('fintech_intensity_score_full', 'std')
    agg['avg_ft_intensity_ctx'] = ('fintech_intensity_score_ctx', 'mean')
    agg['avg_ft_intensity_ctx_std'] = ('fintech_intensity_score_ctx', 'std')

    # --- P. Logit-to-Score 概率映射情感（稳健性检验）---
    # Törnberg (2024). arXiv:2307.13106. DOI: 10.48550/arXiv.2307.13106
    # Shapiro et al. (2022). JoE, 228(2). DOI: 10.1016/j.jeconom.2020.07.053
    #   → Score = P(正面) - P(负面) ∈ [-1, +1]
    #   → 等权 mean/std/sum + VW/HW/MW 加权辅助 sum
    for track in ['_full', '_ctx']:
        agg[f'avg_llm_prob_score{track}'] = (f'llm_prob_score{track}', 'mean')
        agg[f'avg_llm_prob_score_std{track}'] = (f'llm_prob_score{track}', 'std')
        agg[f'llm_prob_score_sum{track}'] = (f'llm_prob_score{track}', 'sum')
        agg[f'llm_prob_score_w_sum{track}'] = (f'llm_prob_score_w{track}', 'sum')
        agg[f'llm_prob_score_mw_sum{track}'] = (f'llm_prob_score_mw{track}', 'sum')
        agg[f'llm_prob_score_hw_sum{track}'] = (f'llm_prob_score_hw{track}', 'sum')

    # Plan v1.37 P2 §5.3.2: 8 new bank-year columns for binary prob_score
    # (avg_{subst,locus}_prob_score_{full,ctx} mean + std). Positive class
    # encoding: 1 = 象征性 / 应用场景 (stata_export.py:40-50). NaN-safe
    # via pandas mean/std (ddof=1 default).
    for track in ['_full', '_ctx']:
        agg[f'avg_subst_prob_score{track}'] = (f'avg_subst_prob_score{track}', 'mean')
        agg[f'avg_subst_prob_score_std{track}'] = (f'avg_subst_prob_score{track}', 'std')
        agg[f'avg_locus_prob_score{track}'] = (f'avg_locus_prob_score{track}', 'mean')
        agg[f'avg_locus_prob_score_std{track}'] = (f'avg_locus_prob_score{track}', 'std')

    return agg


def _compute_tone_gap_tech_app(panel: pd.DataFrame) -> pd.Series:
    """Compute tone_gap_tech_app with min-n confound defense (v3.1.1).

    反向借鉴 tone_gap_sub_symb (encode.py 中 substantiveness 块), 增加
    min(n_tech, n_app) >= 5 过滤防 compositional confound (R8 audit).

    Args:
        panel: 必须含 n_articles_tech, n_articles_app,
               llm_vote_tone_tech_full, llm_vote_tone_app_full
    Returns:
        Float64 Series: gap = tech - app, NaN 当 min < 5
    """
    both_qualified = (panel['n_articles_tech'] >= 5) & (panel['n_articles_app'] >= 5)
    gap_raw = panel['llm_vote_tone_tech_full'] - panel['llm_vote_tone_app_full']
    return gap_raw.where(both_qualified, np.nan)


def aggregate_panel(df: pd.DataFrame) -> pd.DataFrame:
    """按 (target_bank, year) 聚合生成面板。

    核心输出:
      - n_articles: Bank-Year 下的新闻篇数 (Fang & Peress 2009, JF)
      - media_breadth: log(1 + 不同媒体来源数)(信息环境指标)
      - VW Tone: 提及密度加权情感 (Hassan et al. 2019, QJE)
      - _tech / _app 分类指标: 按 innovation_locus 分组的情感均值
    """
    logger.info("=" * 60)
    logger.info("步骤 5: Bank-Year 聚合")
    logger.info("=" * 60)

    # --- 篇章级相对披露密度预计算 ---
    # Abraham, J., Olbert, M., & Vasvari, F. P. (2024). ESG disclosures
    #   in the private equity industry. Journal of Accounting Research, 62(5), 1611-1660.
    #   DOI: 10.1111/1475-679X.12570
    #   → 必须在 groupby 前计算, 否则 mean(a/b) ≠ mean(a)/mean(b) (Jensen 不等式)
    if 'fintech_total_count' in df.columns and 'doc_length' in df.columns:
        _ft_word_ratio = df['fintech_total_count'] / df['doc_length'].replace(0, np.nan)
        df = pd.concat(
            [df, pd.DataFrame({'_ft_word_ratio': _ft_word_ratio}, index=df.index)],
            axis=1,
        ).copy()
        logger.info(f"  _ft_word_ratio 预计算完成: "
                    f"mean={df['_ft_word_ratio'].mean():.6f}, "
                    f"非空={df['_ft_word_ratio'].notna().sum()}")

    # v3.7.2 R8-H1: bool dtype 防御 (防 parquet round-trip 漂移为 object → mean() 退化)
    if 'ctx_is_fallback' in df.columns and df['ctx_is_fallback'].dtype != bool:
        df = df.copy()
        df['ctx_is_fallback'] = df['ctx_is_fallback'].astype('bool')

    agg_dict = build_aggregation_dict(df)

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

    # v3.7.2 R8-H1: 由 _ctx_fallback_count (sum) 派生 n_articles_for_ctx_independence
    # 之所以不在 agg_dict 用 lambda: pandas.groupby.NamedAgg 协议不支持闭包稳定 hash
    if '_ctx_fallback_count' in panel.columns:
        if 'n_articles' in panel.columns:
            panel['n_articles_for_ctx_independence'] = (
                panel['n_articles'].fillna(0).astype(int)
                - panel['_ctx_fallback_count'].fillna(0).astype(int)
            ).astype('int32')
        # 无论是否派生成功, 都必须 drop 内部命名列, 避免下游 underscore-prefix
        # 过滤逻辑 (iv_did.py:634 等) 被干扰
        panel.drop(columns=['_ctx_fallback_count'], inplace=True)

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

    # --- 按 innovation_locus_full 分组聚合（M1 临时单轨; M2 P2 后续展开 _lf/_lc mean 对角线） ---
    if 'innovation_locus_full' in df.columns:
        # 防御性校验：检查非预期值
        valid_cats = {'底层技术', '应用场景'}
        actual_cats = set(df['innovation_locus_full'].dropna().unique())
        unexpected = actual_cats - valid_cats
        if unexpected:
            logger.warning(f"  innovation_locus 含非预期值: {unexpected}，这些文章将不计入分类聚合")

        cat_mapping = [('底层技术', '_tech'), ('应用场景', '_app')]

        for cat_label, suffix in cat_mapping:
            df_cat = df[df['innovation_locus_full'] == cat_label]
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

                # E. Logit-to-Score 概率分数
                src_prob = f'llm_prob_score{track}'
                if src_prob in df_cat.columns:
                    cat_agg[f'llm_prob_score{suffix}{track}'] = (src_prob, 'mean')

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
            panel['n_articles_llm_valid'] > 0,
            panel['n_articles_tech'] / panel['n_articles_llm_valid'],
            np.nan
        )
        panel['app_frac'] = np.where(
            panel['n_articles_llm_valid'] > 0,
            panel['n_articles_app'] / panel['n_articles_llm_valid'],
            np.nan
        )

        # avg_category_confidence
        if 'category_confidence' in df.columns:
            conf = df.groupby(['target_bank', 'year'])['category_confidence'].mean().reset_index()
            conf.columns = ['target_bank', 'year', 'avg_category_confidence']
            panel = panel.merge(conf, on=['target_bank', 'year'], how='left')
        else:
            panel['avg_category_confidence'] = np.nan

        # v7 R6-H: 双轨 × 双维度的 row-level avg confidence 聚合
        # (W&Z 1994/1998 substantiveness + Gomber 2018 locus 信号强度, 由 tone_llms 多模型 avg 而来)
        # v3.2.0 修订: confidence 列名格式为 `<dim>_confidence_<track>`, 与分类列 `<dim>_<track>` 不同
        # v3.4.0: 第三维度 collab_mode (Chesbrough 2003 Open Innovation) 加入
        for _dim_prefix, _short in [('innovation_substantiveness', 'iss'),
                                     ('innovation_locus', 'il'),
                                     ('innovation_collab_mode', 'icm')]:
            for _track in ['_full', '_ctx']:
                _src = f'{_dim_prefix}_confidence{_track}'
                _out = f'avg_{_short}_confidence{_track}'
                if _src in df.columns:
                    _agg = df.groupby(['target_bank', 'year'])[_src].mean().reset_index()
                    _agg.columns = ['target_bank', 'year', _out]
                    panel = panel.merge(_agg, on=['target_bank', 'year'], how='left')
                else:
                    panel[_out] = np.nan

        # 恒等式校验（二分类）
        if all(f'n_articles{s}' in panel.columns for s in ['_tech', '_app']):
            has_news = panel['n_articles_llm_valid'] > 0
            identity_check = (panel.loc[has_news, 'n_articles_llm_valid'] ==
                              panel.loc[has_news, 'n_articles_tech'] +
                              panel.loc[has_news, 'n_articles_app'])
            if identity_check.all():
                logger.info("  ✓ 恒等式校验通过: n_articles == n_articles_tech + n_articles_app")
            else:
                n_fail = (~identity_check).sum()
                logger.warning(f"  ✗ 恒等式校验失败: {n_fail} 行不满足 n_articles == n_articles_tech + n_articles_app")

        # tone_gap_tech_app: 底层技术 vs 应用场景 LLM 投票情感差距 (v3.1.1)
        # 文献: Adner & Kapoor (2010 SMJ); Gomber et al. (2018 JMIS)
        if 'llm_vote_tone_tech_full' in panel.columns and 'llm_vote_tone_app_full' in panel.columns:
            panel['tone_gap_tech_app'] = _compute_tone_gap_tech_app(panel)

        # ── v3.2.0 M2 P2 (plan v14 §2.2): _lc × _ctx 对角线追加 ──
        # Hassan 2019 QJE entity-proximity locus classification + ctx 轨情感
        if 'innovation_locus_ctx' in df.columns:
            for cat_label, suffix in [('底层技术', '_tech_lc_ctx'),
                                      ('应用场景', '_app_lc_ctx')]:
                df_cat_lc = df[df['innovation_locus_ctx'] == cat_label]
                if df_cat_lc.empty:
                    panel[f'n_articles{suffix}'] = 0
                    panel[f'llm_vote_tone{suffix}'] = np.nan
                    panel[f'llm_prob_score{suffix}'] = np.nan
                    continue
                _lc_agg = {
                    f'n_articles{suffix}': ('llm_vote_score_ctx', 'count'),
                    f'llm_vote_tone{suffix}': ('llm_vote_score_ctx', 'mean'),
                    f'llm_prob_score{suffix}': ('llm_prob_score_ctx', 'mean'),
                }
                _lc_p = df_cat_lc.groupby(['target_bank', 'year']).agg(**_lc_agg).reset_index()
                panel = panel.merge(_lc_p, on=['target_bank', 'year'], how='left')

            # 比例 frac (_lc)
            for suffix in ['_tech_lc_ctx', '_app_lc_ctx']:
                if f'n_articles{suffix}' in panel.columns:
                    panel[f'n_articles{suffix}'] = panel[f'n_articles{suffix}'].fillna(0).astype(int)
            # metric-audit 2026-06-02 final: ctx 分子须配 ctx 分母 n_articles_llm_valid_ctx
            # (旧用 full 轨 n_articles_llm_valid → 轨道不对称, frac 越界至 3.0).
            panel['tech_frac_lc'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_tech_lc_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)
            panel['app_frac_lc'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_app_lc_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)

            # tone_gap_tech_app_lc_ctx: ctx 轨同向 gap
            if 'llm_vote_tone_tech_lc_ctx' in panel.columns and 'llm_vote_tone_app_lc_ctx' in panel.columns:
                _both = (panel['n_articles_tech_lc_ctx'] >= 5) & (panel['n_articles_app_lc_ctx'] >= 5)
                _gap = panel['llm_vote_tone_tech_lc_ctx'] - panel['llm_vote_tone_app_lc_ctx']
                panel['tone_gap_tech_app_lc_ctx'] = _gap.where(_both, np.nan)
    else:
        logger.info("  列 'innovation_locus_full' 不存在, 分类聚合将跳过")
        panel['tech_frac'] = np.nan
        panel['app_frac'] = np.nan

    # --- 按 innovation_substantiveness_full 分组聚合（M1 临时单轨; M2 P2 后续展开 _sf/_sc mean 对角线） ---
    if 'innovation_substantiveness_full' in df.columns:
        valid_tts = {'实质性', '象征性'}

        actual_tts = set(df['innovation_substantiveness_full'].dropna().unique())
        unexpected_tt = actual_tts - valid_tts
        if unexpected_tt:
            logger.warning(f"  innovation_substantiveness 含非预期值: {unexpected_tt}，这些文章将不计入分类聚合")

        tt_mapping = [('实质性', '_sub'), ('象征性', '_symb')]

        for tt_label, suffix in tt_mapping:
            df_tt = df[df['innovation_substantiveness_full'] == tt_label]
            if df_tt.empty:
                logger.warning(f"  innovation_substantiveness '{tt_label}' 无文章，跳过 {suffix} 聚合")
                panel[f'n_articles{suffix}'] = 0
                continue

            tt_agg = {}
            tt_agg[f'n_articles{suffix}'] = ('llm_vote_score_full', 'count')

            for track in ['_full', '_ctx']:
                src_vote = f'llm_vote_score{track}'
                if src_vote in df_tt.columns:
                    tt_agg[f'llm_vote_tone{suffix}{track}'] = (src_vote, 'mean')

                # Logit-to-Score 概率分数
                src_prob = f'llm_prob_score{track}'
                if src_prob in df_tt.columns:
                    tt_agg[f'llm_prob_score{suffix}{track}'] = (src_prob, 'mean')

                # v3.1.0: LLM 逐模型 _score 在 _full/_ctx 子集均值 (W&Z 1998 ASQ)
                # 范围依据 (经六轮审核):
                #   - 不补 _cont: 二分类下与 _score 高度共线
                #   - 不补 BERT/词典/IDF: 范围外
                if track in ('_full', '_ctx'):
                    for short in LLM_MODELS:
                        src_llm = f'{short}_score{track}'
                        if src_llm in df_tt.columns:
                            tt_agg[f'{short}_tone{suffix}{track}'] = (src_llm, 'mean')

            tt_panel = df_tt.groupby(['target_bank', 'year']).agg(**tt_agg).reset_index()
            panel = panel.merge(tt_panel, on=['target_bank', 'year'], how='left')
            logger.info(f"  innovation_substantiveness '{tt_label}' 聚合完成: {len(tt_panel):,} 个 Bank-Year, "
                        f"{len(tt_agg)} 个指标")

        # innovation_substantiveness 计数列填充（二分类）
        for suffix in ['_sub', '_symb']:
            col = f'n_articles{suffix}'
            if col in panel.columns:
                panel[col] = panel[col].fillna(0).astype(int)

        # sub_frac / symb_frac（二分类）
        for suffix in ['_sub', '_symb']:
            panel[f'{suffix[1:]}_frac'] = np.where(
                panel['n_articles_llm_valid'] > 0,
                panel[f'n_articles{suffix}'] / panel['n_articles_llm_valid'],
                np.nan
            )

        # 情感纯度差距指标
        # fix(encode-02): 补 min-n>=5 守门 (对齐 _compute_tone_gap_tech_app:814 的 R8 防混淆),
        # 否则单篇 cell 驱动的伪差距进 Table3 机制回归。
        if 'llm_vote_tone_sub_full' in panel.columns and 'llm_vote_tone_symb_full' in panel.columns:
            _sub_symb_qual = (panel['n_articles_sub'] >= 5) & (panel['n_articles_symb'] >= 5)
            panel['tone_gap_sub_symb'] = (
                panel['llm_vote_tone_sub_full'] - panel['llm_vote_tone_symb_full']
            ).where(_sub_symb_qual, np.nan)

        # innovation_substantiveness 恒等式校验（二分类）
        if all(f'n_articles{s}' in panel.columns for s in ['_sub', '_symb']):
            has_news = panel['n_articles_llm_valid'] > 0
            tt_identity = (panel.loc[has_news, 'n_articles_llm_valid'] ==
                           panel.loc[has_news, 'n_articles_sub'] +
                           panel.loc[has_news, 'n_articles_symb'])
            if tt_identity.all():
                logger.info("  ✓ innovation_substantiveness 恒等式校验通过: n_articles == n_articles_sub + n_articles_symb")
            else:
                n_fail_tt = (~tt_identity).sum()
                logger.warning(f"  ✗ innovation_substantiveness 恒等式校验失败: {n_fail_tt} 行")

        # ── v3.2.0 M2 P2 (plan v14 §2.2): _sc × _ctx 对角线追加 ──
        # W&Z 1994/1998 ASQ substantive-symbolic + Hassan 2019 QJE entity-proximity
        if 'innovation_substantiveness_ctx' in df.columns:
            for tt_label, suffix in [('实质性', '_sub_sc_ctx'),
                                     ('象征性', '_symb_sc_ctx')]:
                df_tt_sc = df[df['innovation_substantiveness_ctx'] == tt_label]
                if df_tt_sc.empty:
                    panel[f'n_articles{suffix}'] = 0
                    panel[f'llm_vote_tone{suffix}'] = np.nan
                    panel[f'llm_prob_score{suffix}'] = np.nan
                    continue
                _sc_agg = {
                    f'n_articles{suffix}': ('llm_vote_score_ctx', 'count'),
                    f'llm_vote_tone{suffix}': ('llm_vote_score_ctx', 'mean'),
                    f'llm_prob_score{suffix}': ('llm_prob_score_ctx', 'mean'),
                }
                _sc_p = df_tt_sc.groupby(['target_bank', 'year']).agg(**_sc_agg).reset_index()
                panel = panel.merge(_sc_p, on=['target_bank', 'year'], how='left')

            for suffix in ['_sub_sc_ctx', '_symb_sc_ctx']:
                if f'n_articles{suffix}' in panel.columns:
                    panel[f'n_articles{suffix}'] = panel[f'n_articles{suffix}'].fillna(0).astype(int)
            # metric-audit 2026-06-02 final: ctx 分子配 ctx 分母 (修轨道不对称 frac>1)
            panel['sub_frac_sc'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_sub_sc_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)
            panel['symb_frac_sc'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_symb_sc_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)

            # tone_gap_sub_symb_sc_ctx: ctx 轨情感纯度差距 (fix(encode-02): 补 min-n>=5 守门)
            if 'llm_vote_tone_sub_sc_ctx' in panel.columns and 'llm_vote_tone_symb_sc_ctx' in panel.columns:
                _sub_symb_ctx_qual = (
                    (panel['n_articles_sub_sc_ctx'] >= 5) & (panel['n_articles_symb_sc_ctx'] >= 5)
                )
                panel['tone_gap_sub_symb_sc_ctx'] = (
                    panel['llm_vote_tone_sub_sc_ctx'] - panel['llm_vote_tone_symb_sc_ctx']
                ).where(_sub_symb_ctx_qual, np.nan)
    else:
        logger.info("  列 'innovation_substantiveness_full' 不存在, innovation_substantiveness 分组聚合将跳过")

    # --- v3.4.0: 按 innovation_collab_mode_full 分组聚合 ---
    # 第三维度 (Chesbrough 2003 Open Innovation + Laursen & Salter 2006 SMJ;
    # additive supplementation per Nosek 2018 PNAS, v7 substantiveness/locus 语义不变).
    # 后缀: _indep (自主研发) / _collab (外部协同), 平行于 _sub/_symb 与 _tech/_app.
    if 'innovation_collab_mode_full' in df.columns:
        valid_cms = {'自主研发', '外部协同'}

        actual_cms = set(df['innovation_collab_mode_full'].dropna().unique())
        unexpected_cm = actual_cms - valid_cms
        if unexpected_cm:
            logger.warning(f"  innovation_collab_mode 含非预期值: {unexpected_cm}，这些文章将不计入分类聚合")

        cm_mapping = [('自主研发', '_indep'), ('外部协同', '_collab')]

        for cm_label, suffix in cm_mapping:
            df_cm = df[df['innovation_collab_mode_full'] == cm_label]
            if df_cm.empty:
                logger.warning(f"  innovation_collab_mode '{cm_label}' 无文章，跳过 {suffix} 聚合")
                panel[f'n_articles{suffix}'] = 0
                continue

            cm_agg = {}
            cm_agg[f'n_articles{suffix}'] = ('llm_vote_score_full', 'count')

            for track in ['_full', '_ctx']:
                src_vote = f'llm_vote_score{track}'
                if src_vote in df_cm.columns:
                    cm_agg[f'llm_vote_tone{suffix}{track}'] = (src_vote, 'mean')

                src_prob = f'llm_prob_score{track}'
                if src_prob in df_cm.columns:
                    cm_agg[f'llm_prob_score{suffix}{track}'] = (src_prob, 'mean')

                if track in ('_full', '_ctx'):
                    for short in LLM_MODELS:
                        src_llm = f'{short}_score{track}'
                        if src_llm in df_cm.columns:
                            cm_agg[f'{short}_tone{suffix}{track}'] = (src_llm, 'mean')

            cm_panel = df_cm.groupby(['target_bank', 'year']).agg(**cm_agg).reset_index()
            panel = panel.merge(cm_panel, on=['target_bank', 'year'], how='left')
            logger.info(f"  innovation_collab_mode '{cm_label}' 聚合完成: {len(cm_panel):,} 个 Bank-Year, "
                        f"{len(cm_agg)} 个指标")

        # innovation_collab_mode 计数列填充（二分类）
        for suffix in ['_indep', '_collab']:
            col = f'n_articles{suffix}'
            if col in panel.columns:
                panel[col] = panel[col].fillna(0).astype(int)

        # indep_frac / collab_frac（二分类）
        for suffix in ['_indep', '_collab']:
            panel[f'{suffix[1:]}_frac'] = np.where(
                panel['n_articles_llm_valid'] > 0,
                panel[f'n_articles{suffix}'] / panel['n_articles_llm_valid'],
                np.nan
            )

        # 情感纯度差距指标 (自主 vs 外部协同 LLM 投票情感差)
        # fix(encode-02): 补 min-n>=5 守门 (对齐 tech_app/sub_symb)
        if 'llm_vote_tone_indep_full' in panel.columns and 'llm_vote_tone_collab_full' in panel.columns:
            _indep_collab_qual = (
                (panel['n_articles_indep'] >= 5) & (panel['n_articles_collab'] >= 5)
            )
            panel['tone_gap_indep_collab'] = (
                panel['llm_vote_tone_indep_full'] - panel['llm_vote_tone_collab_full']
            ).where(_indep_collab_qual, np.nan)

        # innovation_collab_mode 恒等式校验（二分类）— F-CR-cell-NA (R6 fix):
        # 旧严格 `n_articles == n_articles_indep + n_articles_collab` 在 LLM 对 collab_mode
        # 维度部分失败时必然破坏 (失败 article 既不入 _indep 也不入 _collab 但仍计入 n_articles).
        # 改为逻辑必然性: `n_articles >= n_articles_indep + n_articles_collab`. 差额 =
        # 上游 collab_mode = NaN 的 articles, 由 v3.5.0 D2 `n_articles_cell_NA_full` 兜底跟踪.
        if all(f'n_articles{s}' in panel.columns for s in ['_indep', '_collab']):
            has_news = panel['n_articles_llm_valid'] > 0
            cm_sum = (panel.loc[has_news, 'n_articles_indep'] +
                      panel.loc[has_news, 'n_articles_collab'])
            n_fail_cm = int((panel.loc[has_news, 'n_articles_llm_valid'] < cm_sum).sum())
            if n_fail_cm == 0:
                cm_gap = int((panel.loc[has_news, 'n_articles_llm_valid'] - cm_sum).sum())
                logger.info(
                    "  ✓ innovation_collab_mode 恒等式校验通过 "
                    f"(LLM collab_mode 部分失败累计 {cm_gap} articles, 由 "
                    "n_articles_cell_NA_full bucket 兜底)"
                )
            else:
                logger.warning(
                    f"  ✗ innovation_collab_mode 恒等式校验失败 (n_articles < "
                    f"sum, 上游 race condition?): {n_fail_cm} 行"
                )

        # ── ctx 轨对角线追加 (与 substantiveness _sc / locus _lc 同模式) ──
        # Chesbrough 2003 + Hassan 2019 QJE entity-proximity
        if 'innovation_collab_mode_ctx' in df.columns:
            for cm_label, suffix in [('自主研发', '_indep_cm_ctx'),
                                     ('外部协同', '_collab_cm_ctx')]:
                df_cm_cm = df[df['innovation_collab_mode_ctx'] == cm_label]
                if df_cm_cm.empty:
                    panel[f'n_articles{suffix}'] = 0
                    panel[f'llm_vote_tone{suffix}'] = np.nan
                    panel[f'llm_prob_score{suffix}'] = np.nan
                    continue
                _cm_agg = {
                    f'n_articles{suffix}': ('llm_vote_score_ctx', 'count'),
                    f'llm_vote_tone{suffix}': ('llm_vote_score_ctx', 'mean'),
                    f'llm_prob_score{suffix}': ('llm_prob_score_ctx', 'mean'),
                }
                _cm_p = df_cm_cm.groupby(['target_bank', 'year']).agg(**_cm_agg).reset_index()
                panel = panel.merge(_cm_p, on=['target_bank', 'year'], how='left')

            for suffix in ['_indep_cm_ctx', '_collab_cm_ctx']:
                if f'n_articles{suffix}' in panel.columns:
                    panel[f'n_articles{suffix}'] = panel[f'n_articles{suffix}'].fillna(0).astype(int)
            # metric-audit 2026-06-02 final: ctx 分子配 ctx 分母 (修轨道不对称 frac>1)
            panel['indep_frac_cm'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_indep_cm_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)
            panel['collab_frac_cm'] = np.where(
                panel['n_articles_llm_valid_ctx'] > 0,
                panel['n_articles_collab_cm_ctx'] / panel['n_articles_llm_valid_ctx'], np.nan)

            if 'llm_vote_tone_indep_cm_ctx' in panel.columns and 'llm_vote_tone_collab_cm_ctx' in panel.columns:
                panel['tone_gap_indep_collab_cm_ctx'] = (
                    panel['llm_vote_tone_indep_cm_ctx'] - panel['llm_vote_tone_collab_cm_ctx']
                )
    else:
        logger.info("  列 'innovation_collab_mode_full' 不存在, innovation_collab_mode 分组聚合将跳过")

    # --- v3.5.0 D2 + D4 派生 (per stage3_v3_5_0_augmentation_plan.md §2.1 / §2.3) ---
    # D2 8-cell decomposition: cell_id_{full,ctx} + 8 cell-count + cross-identity checks
    # D4 cross-track residual: 9 article-level + 18 panel-level + d4_data_quality_flag
    # 走 §7 R10 rollback path: 不拆分 encode.py, 接受 ≈1470 行临时膨胀直至 v3.6.0 refactor.
    try:
        from news_process.pipeline.panel import encode_collab as _ec  # noqa: WPS433
        # CR-17: 默认 baseline 路径从 tests/fixtures/ 改到 data/processed/ (production
        # 不应依赖测试目录; production data 路径与其他 pipeline 输出一致)
        _ctx_baseline_path = os.environ.get(
            'V3_4_0_CTX_COVERAGE_BASELINE',
            'data/processed/v3_4_0_ctx_coverage_baseline.json',
        )
        _v3_5_diag = _ec.apply_v3_5_0(df, panel, ctx_baseline_path=_ctx_baseline_path)
        panel.attrs['v3_5_0_diagnostics'] = _v3_5_diag
        logger.info(
            f"  ✓ v3.5.0 D2+D4 派生完成: cell_id ✓ + residual cols "
            f"{len(_v3_5_diag.get('v3_5_0_residual_articles_added', []))}"
        )

        # v3.5.1 A1 + A3 supplementation (与 apply_v3_5_0 并存, 修 C2).
        # idempotent panel schema 加列; 失败 graceful (不 raise, 保证 v3.5.0 baseline 不破).
        try:
            _v3_5_1_diag = _ec.apply_v3_5_1(df, panel, prompt_v8_sha256=None)
            panel.attrs['v3_5_1_diagnostics'] = _v3_5_1_diag
            n_clarity = len(_v3_5_1_diag.get('v3_5_1_clarity_added', []))
            n_ni = len(_v3_5_1_diag.get('v3_5_1_num_intensity_added', []))
            logger.info(
                f"  ✓ v3.5.1 A1+A3 派生完成: clarity {n_clarity} cols + num_intensity {n_ni} cols; "
                f"sidecar: {_v3_5_1_diag.get('sidecar_path', '?')}"
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"  ⚠ v3.5.1 A1+A3 派生 graceful skip: {e}")

        # v3.5.2 PR #2/#3 LM 4 subdicts + FLS panel-level aggregation
        # (O2 sample-run finding 2026-05-25: 关闭 CLAUDE.md 顶部声明 "stage 22
        # +10 panel 列" 与 disk 实际 0 panel 列的 gap; article-level 8 LM + 2 FLS
        # 已在 stage 22 _dual_analyze 产出, 缺 panel-agg).
        try:
            _v3_5_2_diag = _ec.apply_v3_5_2(df, panel)
            panel.attrs['v3_5_2_diagnostics'] = _v3_5_2_diag
            if _v3_5_2_diag.get('v3_5_2_skipped_reason'):
                logger.warning(f"  ⚠ v3.5.2 LM+FLS panel-agg skip: {_v3_5_2_diag['v3_5_2_skipped_reason']}")
            else:
                logger.info(
                    f"  ✓ v3.5.2 LM+FLS panel-agg 完成: "
                    f"LM {len(_v3_5_2_diag.get('v3_5_2_lm_added', []))} cols + "
                    f"FLS {len(_v3_5_2_diag.get('v3_5_2_fls_added', []))} cols"
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"  ⚠ v3.5.2 LM+FLS panel-agg graceful skip: {e}")
    except Exception:  # noqa: BLE001
        # CR-16: logger.exception 自动 attach traceback, 比 logger.error + 手工 raise 标准
        logger.exception("  ✗ v3.5.0 D2+D4 派生失败")
        raise


    # 新闻覆盖量对数
    panel_new_cols = {
        'ln_news_coverage': np.log1p(panel['n_articles']),
    }

    # --- Value-weighted Tone 计算 (Hassan et al. 2019, QJE; 双轨) ---
    # 公式: VW_tone_i = Σ(mention_density_j × tone_j) / Σ(mention_density_j)
    # 其中 j 遍历 Bank i 在 Year t 下的所有文章。
    # 提及密度越高的文章对聚合情感的贡献越大,
    # 这反映了"银行作为核心主题的文章应有更大权重"的直觉。
    if 'sum_mention_density' in panel.columns:
        denom = panel['sum_mention_density'].replace(0, np.nan)
        for track in ['_full', '_ctx']:
            if f'llm_vote_score_w_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_tone_vw{track}'] = panel[f'llm_vote_score_w_sum{track}'] / denom
            if f'llm_vote_cont_w_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_cont_vw{track}'] = panel[f'llm_vote_cont_w_sum{track}'] / denom
            for short in LLM_MODELS:
                w_col = f'{short}_score_w_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{short}_tone_vw{track}'] = panel[w_col] / denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_w_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{d}_tone_vw{track}'] = panel[w_col] / denom
            # IDF VW Tone (Gentzkow, Kelly & Taddy 2019, JEL)
            for d in DICT_NAMES:
                w_col = f'{d}_idf_score_w_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{d}_idf_tone_vw{track}'] = panel[w_col] / denom
            for b in BERT_MODELS:
                w_pos = f'{b}_正面_w_sum{track}'
                w_neg = f'{b}_负面_w_sum{track}'
                if w_pos in panel.columns:
                    panel_new_cols[f'{b}_pos_vw{track}'] = panel[w_pos] / denom
                if w_neg in panel.columns:
                    panel_new_cols[f'{b}_neg_vw{track}'] = panel[w_neg] / denom
            # Logit-to-Score 概率分数 VW
            w_prob = f'llm_prob_score_w_sum{track}'
            if w_prob in panel.columns:
                panel_new_cols[f'llm_vote_tone_vw_prob{track}'] = panel[w_prob] / denom
        logger.info(f"  已计算 Value-weighted Tone 指标（双轨）")

    # --- MW Tone (媒体权威性加权, Holzman et al. 2023, TAR) ---
    if 'sum_media_authority_weight' in panel.columns:
        mw_denom = panel['sum_media_authority_weight'].replace(0, np.nan)
        for track in ['_full', '_ctx']:
            if f'llm_vote_score_mw_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_tone_mw{track}'] = (
                    panel[f'llm_vote_score_mw_sum{track}'] / mw_denom)
            if f'llm_vote_cont_mw_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_cont_mw{track}'] = (
                    panel[f'llm_vote_cont_mw_sum{track}'] / mw_denom)
            for short in LLM_MODELS:
                w_col = f'{short}_score_mw_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{short}_tone_mw{track}'] = panel[w_col] / mw_denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_mw_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{d}_tone_mw{track}'] = panel[w_col] / mw_denom
                w_idf = f'{d}_idf_score_mw_sum{track}'
                if w_idf in panel.columns:
                    panel_new_cols[f'{d}_idf_tone_mw{track}'] = panel[w_idf] / mw_denom
            for b in BERT_MODELS:
                for label, sfx in [('_正面', '_pos'), ('_负面', '_neg')]:
                    w_col = f'{b}{label}_mw_sum{track}'
                    if w_col in panel.columns:
                        panel_new_cols[f'{b}{sfx}_mw{track}'] = panel[w_col] / mw_denom
            # Logit-to-Score 概率分数 MW
            w_prob = f'llm_prob_score_mw_sum{track}'
            if w_prob in panel.columns:
                panel_new_cols[f'llm_vote_tone_mw_prob{track}'] = panel[w_prob] / mw_denom
        logger.info(f"  已计算 Media-Authority-weighted Tone 指标（双轨）")

    # --- HW Tone (跟风衰减加权, Tetlock 2011, JF) ---
    # v3.6.0 (Plan E P1 B3): hw_denom 按 track 双轨独立 (Edwards 2001 ORM
    # measurement-treatment matching) — 修正 v3.5.0 错配 (全文 sum 当分母,
    # 同时除给 _full / _ctx 两轨)。
    # remove-title-track: 原 _title HW fallback 轨已取消 (标题轨停产)。
    # 轨道映射:
    #   _full  → sum_herd_weight_full  (双轨列)
    #   _ctx   → sum_herd_weight_ctx   (双轨列)
    # Round 1 M1 清理 dead code: build_aggregation_dict 永远生成 sum_herd_weight_full
    # + _ctx (legacy 单列 silently 映射到双轨 key, 由 build_aggregation_dict 内打 WARN).
    # 故 _has_legacy_sum 永远 False, 删除该分支.
    if ('sum_herd_weight_full' in panel.columns and
            'sum_herd_weight_ctx' in panel.columns):
        hw_denom_full = panel['sum_herd_weight_full'].replace(0, np.nan)
        hw_denom_ctx = panel['sum_herd_weight_ctx'].replace(0, np.nan)
        hw_denom_by_track = {
            '_full': hw_denom_full,
            '_ctx': hw_denom_ctx,
        }
        for track in ['_full', '_ctx']:
            hw_denom = hw_denom_by_track[track]
            if f'llm_vote_score_hw_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_tone_hw{track}'] = (
                    panel[f'llm_vote_score_hw_sum{track}'] / hw_denom)
            if f'llm_vote_cont_hw_sum{track}' in panel.columns:
                panel_new_cols[f'llm_vote_cont_hw{track}'] = (
                    panel[f'llm_vote_cont_hw_sum{track}'] / hw_denom)
            for short in LLM_MODELS:
                w_col = f'{short}_score_hw_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{short}_tone_hw{track}'] = panel[w_col] / hw_denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_hw_sum{track}'
                if w_col in panel.columns:
                    panel_new_cols[f'{d}_tone_hw{track}'] = panel[w_col] / hw_denom
                w_idf = f'{d}_idf_score_hw_sum{track}'
                if w_idf in panel.columns:
                    panel_new_cols[f'{d}_idf_tone_hw{track}'] = panel[w_idf] / hw_denom
            for b in BERT_MODELS:
                for label, sfx in [('_正面', '_pos'), ('_负面', '_neg')]:
                    w_col = f'{b}{label}_hw_sum{track}'
                    if w_col in panel.columns:
                        panel_new_cols[f'{b}{sfx}_hw{track}'] = panel[w_col] / hw_denom
            # Logit-to-Score 概率分数 HW
            w_prob = f'llm_prob_score_hw_sum{track}'
            if w_prob in panel.columns:
                panel_new_cols[f'llm_vote_tone_hw_prob{track}'] = panel[w_prob] / hw_denom
        logger.info("  已计算 Herd-Decay-weighted Tone 指标 (双轨独立分母)")

    # remove-title-track: tone_gap_title_full / prob_gap_title_full 已取消 (标题轨停产)

    if panel_new_cols:
        panel = pd.concat(
            [panel, pd.DataFrame(panel_new_cols, index=panel.index)],
            axis=1,
        ).copy()

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
    # F5 fix (2026-05-30): 旧 `endswith('_sum')` 匹配 0 列 — 每个加权和分子都带
    # 轨道后缀 (_sum_full / _sum_ctx), 末尾是轨道而非裸 '_sum'。
    # 零新闻 bank-year 的和是 Σ over ∅ = 0, 故这些分子列应填 0 (符合"计数/和类填 0"
    # 契约); 被消费的均值/比例列不在此匹配内, 正确保持 NaN。
    sum_cols = [c for c in panel.columns
                if re.search(r'_sum_(full|ctx|title)$', c)]
    count_cols = ['sum_mention_density', 'sum_doc_length', 'sum_target_mentions',
                  'sum_media_authority_weight']
    # audit-fixes 2026-05-29 (L1): 此前列出 bare 名 'pos_count'/'neg_count'/
    # 'pos_count_vw'/'neg_count_vw', 但聚合只产出带轨道后缀的名
    # (pos_count_full / pos_count_vw_full / ...), bare 名永不匹配 →
    # 零新闻 bank-year 的计数列残留 NaN 而非 0 (与本段"计数类填 0"的契约相悖,
    # 导出的 .dta 计数列在无覆盖行显示 . 而非 0)。改用 regex 匹配实际后缀名。
    # F4 fix (2026-05-30): 旧锚定式 ^(pos|neg)_count... 只覆盖 12 个 bare-family
    # 计数列; 逐模型/逐词典/逐 BERT/symb-sub 等新闻计数
    # (gpt54nano_pos_count_full / jiang_2021_neg_count_ctx / pos_symb_count_full /
    # neg_sub_count_full / *_hc_count* ...) 永不匹配 → 零新闻格残留 NaN 而非 0。
    # 改为匹配任意 *_count(_vw)?_<track>; 排除 peer-group 计数 (llm_peer_count*,
    # 在零自有新闻时合法非零) 与实体属性均值 (avg/max_bank_count, 无轨道后缀, 正确保持 NaN)。
    _count_pat = re.compile(r'_count(_vw)?_(full|ctx|title)$')
    suffixed_count_cols = [c for c in panel.columns
                           if _count_pat.search(c) and 'peer' not in c]
    zero_fill_cols = zero_fill_patterns + sum_cols + count_cols + suffixed_count_cols

    for col in zero_fill_cols:
        if col in panel.columns:
            panel[col] = panel[col].fillna(0)

    # --- 分类维度计数列填充为 0 ---
    # zero_fill_patterns 中的 'n_articles' 为精确匹配，不会捕获 n_articles_tech / n_articles_app
    for suffix in ['_tech', '_app']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # --- innovation_substantiveness 分类维度计数列填充为 0（独立循环，不追加到 innovation_locus） ---
    for suffix in ['_sub', '_symb']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # --- v3.4.0: innovation_collab_mode 分类维度计数列填充为 0 (Chesbrough 2003) ---
    for suffix in ['_indep', '_collab']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # 其余 NaN 列保持不变（均值、比例、离散度等由 Stata 处理）
    # tech_frac / app_frac / sub_frac / symb_frac / indep_frac / collab_frac / avg_category_confidence:
    # 零新闻行保持 NaN

    logger.info(f"  完全笛卡尔积: {len(all_banks)} 银行 × {len(all_years)} 年 = {rows_after:,} 行")
    logger.info(f"  原有观测值: {rows_before:,} 行")
    fill_pct = filled_count / rows_after if rows_after > 0 else 0
    logger.info(f"  填充的零新闻观测: {filled_count:,} 行 ({fill_pct:.1%})")

    return panel

