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

import os
import re
import json
import time
import warnings

import numpy as np
import pandas as pd

from utils.helpers import (
    load_config, setup_logging
)

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
    for track in ['_full', '_ctx', '_title']:
        # _title 轨道可能因未配置 title_sentiment_prompt_template 而不存在
        if f'llm_sentiment{track}' not in df.columns:
            logger.info(f"  跳过 {track} 轨道编码（列 llm_sentiment{track} 不存在）")
            continue
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
    for track in ['_full', '_ctx', '_title']:
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

    for track in ['_full', '_ctx', '_title']:
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

    # --- J. LLM 置信度聚合 (Shapiro, Sudhof & Wilson 2022, JoE;
    #        Baker et al. 2024, JAR — 信号清晰度/衰减偏误调节) ---
    # 学术依据: 情感度量的信噪比直接影响回归系数的估计精度
    # (Shapiro et al. 2022, Section 4: attenuation bias correction)
    # 置信度越低 → 测量误差越大 → Tone 对因变量的估计系数向零衰减
    for track in ['_full', '_ctx', '_title']:
        # 三模型宏平均置信度 → Bank-Year 均值 & 标准差
        agg[f'avg_llm_conf{track}'] = (f'avg_llm_conf{track}', 'mean')
        agg[f'avg_llm_conf_std{track}'] = (f'avg_llm_conf{track}', 'std')
        # 逐模型置信度 → Bank-Year 均值 (稳健性分解)
        for short in LLM_MODELS:
            conf_src = f'{short}_sentiment_confidence{track}'
            agg[f'avg_{short}_conf{track}'] = (conf_src, 'mean')

    # --- E. 新闻覆盖量 & 稳健性辅助（无需双轨） ---
    # --- G2. LLM 前瞻性交叉验证 (AI 时态判断, 与词典法 G 互为稳健性检验) ---
    agg['avg_is_forward_looking'] = ('is_forward_looking', 'mean')
    agg['sum_is_forward_looking'] = ('is_forward_looking', 'sum')
    agg['n_articles'] = ('llm_vote_score_full', 'count')
    agg['headline_frac'] = ('in_title', 'mean')
    agg['multi_bank_frac'] = ('is_multi_bank', 'mean')
    agg['avg_bank_count'] = ('bank_count', 'mean')
    agg['max_bank_count'] = ('bank_count', 'max')
    agg['avg_agreement_rate_full'] = ('llm_agreement_rate_full', 'mean')
    agg['avg_agreement_rate_ctx'] = ('llm_agreement_rate_ctx', 'mean')
    agg['avg_agreement_rate_title'] = ('llm_agreement_rate_title', 'mean')

    # --- F. Value-weighted 辅助列 (Hassan et al. 2019, QJE; Sautner et al. 2023, JF) ---
    agg['sum_mention_density'] = ('mention_density', 'sum')
    agg['sum_doc_length'] = ('doc_length', 'sum')
    agg['avg_doc_length'] = ('doc_length', 'mean')
    agg['sum_target_mentions'] = ('target_bank_mention_count', 'sum')
    for track in ['_full', '_ctx', '_title']:
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
    agg['avg_herd_weight'] = ('herd_weight', 'mean')
    agg['min_herd_weight'] = ('herd_weight', 'min')
    # --- F5. 跟风衰减加权聚合 (Tetlock 2011, JF) ---
    agg['sum_herd_weight'] = ('herd_weight', 'sum')
    for track in ['_full', '_ctx', '_title']:
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
    for track in ['_full', '_ctx', '_title']:
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
        valid_cats = {'底层技术', '应用场景', '混合型'}
        actual_cats = set(df['fintech_category'].dropna().unique())
        unexpected = actual_cats - valid_cats
        if unexpected:
            logger.warning(f"  fintech_category 含非预期值: {unexpected}，这些文章将不计入分类聚合")

        cat_mapping = [('底层技术', '_tech'), ('应用场景', '_app'), ('混合型', '_mix')]

        for cat_label, suffix in cat_mapping:
            df_cat = df[df['fintech_category'] == cat_label]
            if df_cat.empty:
                logger.warning(f"  分类 '{cat_label}' 无文章，跳过 {suffix} 聚合")
                panel[f'n_articles{suffix}'] = 0
                continue

            # 构建分类聚合字典（仅 mean，不含 sum/std/VW）
            cat_agg = {}
            cat_agg[f'n_articles{suffix}'] = ('llm_vote_score_full', 'count')

            for track in ['_full', '_ctx', '_title']:
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
        for suffix in ['_tech', '_app', '_mix']:
            col = f'n_articles{suffix}'
            if col in panel.columns:
                panel[col] = panel[col].fillna(0).astype(int)

        # tech_frac / app_frac / mix_frac
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
        panel['mix_frac'] = np.where(
            panel['n_articles'] > 0,
            panel['n_articles_mix'] / panel['n_articles'],
            np.nan
        )

        # avg_category_confidence
        if 'category_confidence' in df.columns:
            conf = df.groupby(['target_bank', 'year'])['category_confidence'].mean().reset_index()
            conf.columns = ['target_bank', 'year', 'avg_category_confidence']
            panel = panel.merge(conf, on=['target_bank', 'year'], how='left')
        else:
            panel['avg_category_confidence'] = np.nan

        # 恒等式校验（三分类）
        if all(f'n_articles{s}' in panel.columns for s in ['_tech', '_app', '_mix']):
            has_news = panel['n_articles'] > 0
            identity_check = (panel.loc[has_news, 'n_articles'] ==
                              panel.loc[has_news, 'n_articles_tech'] +
                              panel.loc[has_news, 'n_articles_app'] +
                              panel.loc[has_news, 'n_articles_mix'])
            if identity_check.all():
                logger.info("  ✓ 恒等式校验通过: n_articles == n_articles_tech + n_articles_app + n_articles_mix")
            else:
                n_fail = (~identity_check).sum()
                logger.warning(f"  ✗ 恒等式校验失败: {n_fail} 行不满足 n_articles == n_articles_tech + n_articles_app + n_articles_mix")
    else:
        logger.info("  列 'fintech_category' 不存在, 分类聚合将跳过")
        panel['tech_frac'] = np.nan
        panel['app_frac'] = np.nan

    # --- 按 text_type 分组聚合（实质性 / 描述性 / 混合型） ---
    if 'text_type' in df.columns:
        valid_tts = {'实质性', '描述性', '混合型'}
        actual_tts = set(df['text_type'].dropna().unique())
        unexpected_tt = actual_tts - valid_tts
        if unexpected_tt:
            logger.warning(f"  text_type 含非预期值: {unexpected_tt}，这些文章将不计入分类聚合")

        tt_mapping = [('实质性', '_sub'), ('描述性', '_desc'), ('混合型', '_tmix')]

        for tt_label, suffix in tt_mapping:
            df_tt = df[df['text_type'] == tt_label]
            if df_tt.empty:
                logger.warning(f"  text_type '{tt_label}' 无文章，跳过 {suffix} 聚合")
                panel[f'n_articles{suffix}'] = 0
                continue

            tt_agg = {}
            tt_agg[f'n_articles{suffix}'] = ('llm_vote_score_full', 'count')

            for track in ['_full', '_ctx', '_title']:
                src_vote = f'llm_vote_score{track}'
                if src_vote in df_tt.columns:
                    tt_agg[f'llm_vote_tone{suffix}{track}'] = (src_vote, 'mean')

            tt_panel = df_tt.groupby(['target_bank', 'year']).agg(**tt_agg).reset_index()
            panel = panel.merge(tt_panel, on=['target_bank', 'year'], how='left')
            logger.info(f"  text_type '{tt_label}' 聚合完成: {len(tt_panel):,} 个 Bank-Year, "
                        f"{len(tt_agg)} 个指标")

        # text_type 计数列填充
        for suffix in ['_sub', '_desc', '_tmix']:
            col = f'n_articles{suffix}'
            if col in panel.columns:
                panel[col] = panel[col].fillna(0).astype(int)

        # sub_frac / desc_frac / tmix_frac
        for suffix in ['_sub', '_desc', '_tmix']:
            panel[f'{suffix[1:]}_frac'] = np.where(
                panel['n_articles'] > 0,
                panel[f'n_articles{suffix}'] / panel['n_articles'],
                np.nan
            )

        # 情感纯度差距指标
        if 'llm_vote_tone_sub_full' in panel.columns and 'llm_vote_tone_desc_full' in panel.columns:
            panel['tone_gap_sub_desc'] = (
                panel['llm_vote_tone_sub_full'] - panel['llm_vote_tone_desc_full']
            )

        # text_type 恒等式校验
        if all(f'n_articles{s}' in panel.columns for s in ['_sub', '_desc', '_tmix']):
            has_news = panel['n_articles'] > 0
            tt_identity = (panel.loc[has_news, 'n_articles'] ==
                           panel.loc[has_news, 'n_articles_sub'] +
                           panel.loc[has_news, 'n_articles_desc'] +
                           panel.loc[has_news, 'n_articles_tmix'])
            if tt_identity.all():
                logger.info("  ✓ text_type 恒等式校验通过: n_articles == n_articles_sub + n_articles_desc + n_articles_tmix")
            else:
                n_fail_tt = (~tt_identity).sum()
                logger.warning(f"  ✗ text_type 恒等式校验失败: {n_fail_tt} 行")
    else:
        logger.info("  列 'text_type' 不存在, text_type 分组聚合将跳过")

    # 新闻覆盖量对数
    panel['ln_news_coverage'] = np.log1p(panel['n_articles'])

    # --- Value-weighted Tone 计算 (Hassan et al. 2019, QJE; 双轨) ---
    # 公式: VW_tone_i = Σ(mention_density_j × tone_j) / Σ(mention_density_j)
    # 其中 j 遍历 Bank i 在 Year t 下的所有文章。
    # 提及密度越高的文章对聚合情感的贡献越大,
    # 这反映了"银行作为核心主题的文章应有更大权重"的直觉。
    if 'sum_mention_density' in panel.columns:
        denom = panel['sum_mention_density'].replace(0, np.nan)
        for track in ['_full', '_ctx', '_title']:
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
        for track in ['_full', '_ctx', '_title']:
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

    # --- HW Tone (跟风衰减加权, Tetlock 2011, JF) ---
    if 'sum_herd_weight' in panel.columns:
        hw_denom = panel['sum_herd_weight'].replace(0, np.nan)
        for track in ['_full', '_ctx', '_title']:
            if f'llm_vote_score_hw_sum{track}' in panel.columns:
                panel[f'llm_vote_tone_hw{track}'] = (
                    panel[f'llm_vote_score_hw_sum{track}'] / hw_denom)
            if f'llm_vote_cont_hw_sum{track}' in panel.columns:
                panel[f'llm_vote_cont_hw{track}'] = (
                    panel[f'llm_vote_cont_hw_sum{track}'] / hw_denom)
            for short in LLM_MODELS:
                w_col = f'{short}_score_hw_sum{track}'
                if w_col in panel.columns:
                    panel[f'{short}_tone_hw{track}'] = panel[w_col] / hw_denom
            for d in DICT_NAMES:
                w_col = f'{d}_score_hw_sum{track}'
                if w_col in panel.columns:
                    panel[f'{d}_tone_hw{track}'] = panel[w_col] / hw_denom
                w_idf = f'{d}_idf_score_hw_sum{track}'
                if w_idf in panel.columns:
                    panel[f'{d}_idf_tone_hw{track}'] = panel[w_idf] / hw_denom
            for b in BERT_MODELS:
                for label, sfx in [('_正面', '_pos'), ('_负面', '_neg')]:
                    w_col = f'{b}{label}_hw_sum{track}'
                    if w_col in panel.columns:
                        panel[f'{b}{sfx}_hw{track}'] = panel[w_col] / hw_denom
        logger.info(f"  已计算 Herd-Decay-weighted Tone 指标（双轨）")

    # --- 标题-全文情感缺口（B1-2 Step 4d） ---
    # 衡量"标题党/软文嫌疑": gap越大→标题情感偏离全文→投资者可能过度反应
    if 'llm_vote_tone_title' in panel.columns and 'llm_vote_tone_full' in panel.columns:
        panel['tone_gap_title_full'] = (
            panel['llm_vote_tone_title'] - panel['llm_vote_tone_full']
        )
        logger.info("  已计算 tone_gap_title_full (标题-全文情感缺口)")

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
                  'sum_media_authority_weight']
    # 动态匹配所有 sum_fl_count 列（三轨: _full/_ctx/_title）
    count_cols += [c for c in panel.columns if c.startswith('sum_fl_count')]
    zero_fill_cols = zero_fill_patterns + sum_cols + count_cols

    for col in zero_fill_cols:
        if col in panel.columns:
            panel[col] = panel[col].fillna(0)

    # --- 分类维度计数列填充为 0 ---
    # zero_fill_patterns 中的 'n_articles' 为精确匹配，不会捕获 n_articles_tech / n_articles_app / n_articles_mix
    for suffix in ['_tech', '_app', '_mix']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # --- text_type 分类维度计数列填充为 0（独立循环，不追加到 fintech_category） ---
    for suffix in ['_sub', '_desc', '_tmix']:
        col = f'n_articles{suffix}'
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # 其余 NaN 列保持不变（均值、比例、离散度等由 Stata 处理）
    # tech_frac / app_frac / mix_frac / sub_frac / desc_frac / tmix_frac / avg_category_confidence: 零新闻行保持 NaN

    logger.info(f"  完全笛卡尔积: {len(all_banks)} 银行 × {len(all_years)} 年 = {rows_after:,} 行")
    logger.info(f"  原有观测值: {rows_before:,} 行")
    fill_pct = filled_count / rows_after if rows_after > 0 else 0
    logger.info(f"  填充的零新闻观测: {filled_count:,} 行 ({fill_pct:.1%})")

    return panel

