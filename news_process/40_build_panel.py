"""
40_build_panel.py — Bank-Year 面板数据构建
==========================================

将篇章级新闻情感分析数据（23_bert_tone.parquet）转化为 **Bank-Year 面板数据**,
遵循 Tetlock et al. (2008, JF) 范式, 为 Stata 回归提供出版就绪数据集。

核心设计原则 — 先分后合（Disaggregate-then-Aggregate）:
  情感指标不在篇章级预先综合, 而是在 Bank-Year 聚合阶段对每个模型/词典
  分别聚合, 最后在面板层级计算综合指标。

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

# LLM 模型 short_name 列表（从 tone_llm_processing.models 读取）
_llm_cfg = CONFIG.get('tone_llm_processing', {}).get('models', [])
LLM_MODELS = [m['short_name'] for m in _llm_cfg] if _llm_cfg else ['gpt5nano', 'gemini3', 'claude4h']

# 词典名列表
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
    """构建 GroupBy 聚合字典（双轨）。"""
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

        # --- C2. 词典法 IDF 加权稳健性检验 (Gentzkow et al. 2019) ---
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

        # --- G. 前瞻性陈述 (Li 2010, Journal of Accounting Research) ---
        agg[f'avg_fl_ratio{track}'] = (f'forward_looking_ratio{track}', 'mean')
        agg[f'avg_fl_ratio_std{track}'] = (f'forward_looking_ratio{track}', 'std')
        agg[f'sum_fl_count{track}'] = (f'forward_looking_count{track}', 'sum')

        # --- H. 文本可读性控制变量 (Loughran & McDonald 2014, Journal of Finance) ---
        agg[f'avg_sent_len{track}'] = (f'avg_sentence_len{track}', 'mean')
        agg[f'avg_ttr{track}'] = (f'type_token_ratio{track}', 'mean')
        agg[f'avg_cpw{track}'] = (f'char_per_word{track}', 'mean')

        # --- I. 正/负面词频分离 (Berger et al. 2024, Appendix S6;
        #        Loughran & McDonald 2011, Journal of Finance) ---
        agg[f'avg_pos_ratio{track}'] = (f'pos_ratio{track}', 'mean')
        agg[f'avg_neg_ratio{track}'] = (f'neg_ratio{track}', 'mean')
        agg[f'avg_pos_ratio_std{track}'] = (f'pos_ratio{track}', 'std')
        agg[f'avg_neg_ratio_std{track}'] = (f'neg_ratio{track}', 'std')

    # --- E. 新闻覆盖量 & 稳健性辅助（无需双轨） ---
    agg['n_articles'] = ('llm_vote_score_full', 'count')
    agg['headline_frac'] = ('in_title', 'mean')
    agg['multi_bank_frac'] = ('is_multi_bank', 'mean')
    agg['avg_bank_count'] = ('bank_count', 'mean')
    agg['max_bank_count'] = ('bank_count', 'max')
    agg['avg_agreement_rate_full'] = ('llm_agreement_rate_full', 'mean')
    agg['avg_agreement_rate_ctx'] = ('llm_agreement_rate_ctx', 'mean')

    # --- F. Value-weighted 辅助列 (Hassan 2019, Sautner 2023 范式) ---
    agg['sum_mention_density'] = ('mention_density', 'sum')
    agg['sum_doc_length'] = ('doc_length', 'sum')
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
        # --- F2. IDF VW 聚合 (Gentzkow et al. 2019 稳健性检验) ---
        for d in DICT_NAMES:
            agg[f'{d}_idf_score_w_sum{track}'] = (f'{d}_idf_score_w{track}', 'sum')
        for b in BERT_MODELS:
            agg[f'{b}_正面_w_sum{track}'] = (f'{b}_正面_w{track}', 'sum')
            agg[f'{b}_负面_w_sum{track}'] = (f'{b}_负面_w{track}', 'sum')

    return agg


def aggregate_panel(df: pd.DataFrame) -> pd.DataFrame:
    """按 (target_bank, year) 聚合生成面板。"""
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

    # --- tech_frac ---
    if 'is_fintech_news' in df.columns:
        tech_frac = df.groupby(['target_bank', 'year'])['is_fintech_news'].mean().reset_index()
        tech_frac.columns = ['target_bank', 'year', 'tech_frac']
        panel = panel.merge(tech_frac, on=['target_bank', 'year'], how='left')
    else:
        logger.info("  列 'is_fintech_news' 不存在, tech_frac 将为 NaN")
        panel['tech_frac'] = np.nan

    # 新闻覆盖量对数
    panel['ln_news_coverage'] = np.log1p(panel['n_articles'])

    # --- Value-weighted Tone 计算 (VW, Hassan 2019 范式, 双轨) ---
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
            # IDF VW Tone (Gentzkow et al. 2019 稳健性检验)
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

    logger.info(f"  聚合后面板行数: {panel.shape[0]:,}")
    logger.info(f"  唯一银行数: {panel['target_bank'].nunique()}")
    logger.info(f"  年份范围: {panel['year'].min()} - {panel['year'].max()}")
    return panel


# ============================================================================
# 6. 面板平衡与缺失期填充
# ============================================================================

def balance_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """构建平衡面板: 银行 × 年份笛卡尔积 + 科学填充。"""
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
                  'sum_fl_count_full', 'sum_fl_count_ctx']
    zero_fill_cols = zero_fill_patterns + sum_cols + count_cols

    for col in zero_fill_cols:
        if col in panel.columns:
            panel[col] = panel[col].fillna(0)

    # 其余 NaN 列保持不变（均值、比例、离散度等由 Stata 处理）

    logger.info(f"  完全笛卡尔积: {len(all_banks)} 银行 × {len(all_years)} 年 = {rows_after:,} 行")
    logger.info(f"  原有观测值: {rows_before:,} 行")
    fill_pct = filled_count / rows_after if rows_after > 0 else 0
    logger.info(f"  填充的零新闻观测: {filled_count:,} 行 ({fill_pct:.1%})")

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

        # --- 词典法 IDF 综合 (Gentzkow et al. 2019 稳健性检验) ---
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

    logger.info(f"  生成双轨综合指标完成")
    return panel


# ============================================================================
# 8. 诊断统计量
# ============================================================================

def log_diagnostics(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """输出面板诊断统计。"""
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
            panel_stata.to_stata(dta_path, write_index=False, version=118)
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
            # 词典 IDF (Gentzkow et al. 2019 稳健性检验)
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

    # --- 4. 时间解析 ---
    df = parse_time(df)

    # 保存展开后文章级数据引用
    df_exploded = df.copy()

    # --- 5. Bank-Year 聚合 ---
    panel = aggregate_panel(df)

    # --- 6. 面板平衡 ---
    panel = balance_panel(panel)

    # --- 7. 综合指标 ---
    panel = compute_composite_indicators(panel)

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
        }
    )

    logger.info("40_build_panel 执行完毕 ✓")


if __name__ == '__main__':
    main()
