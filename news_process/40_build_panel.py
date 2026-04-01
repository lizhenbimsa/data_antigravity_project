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
  - tone_mw:         媒体权威性加权均值 (MW, Holzman et al., 2023, JAR)
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
# 3c. 媒体权威性加权 (Holzman, Miller & Twedt 2023, JAR, Appendix A)
# ============================================================================

def compute_media_authority_weights(df: pd.DataFrame) -> pd.DataFrame:
    """步骤 3c: 媒体权威性加权。

    学术依据:
      Holzman, E.R., Miller, B.P. & Twedt, B.J. (2023).
      "Curbing Enthusiasm: Media Sentiment and the Disciplining Role
      of Quarterly Earnings Announcements."
      Journal of Accounting Research, 61(2), 429-473.
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
    logger.info("步骤 3c: 媒体权威性加权 (Holzman et al. 2023, JAR)")
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

    # --- F3. 媒体权威性加权聚合 (Holzman et al. 2023, JAR) ---
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

    # --- MW Tone (媒体权威性加权, Holzman et al. 2023, JAR) ---
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

        # --- MW 综合指标 (Holzman et al. 2023, JAR) ---
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
                # 媒体权威性加权 (Holzman et al. 2023, JAR)
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

    # --- 3c. 媒体权威性加权列预计算 (Holzman et al. 2023, JAR) ---
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

    # --- 8. 诊断统计 ---
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
