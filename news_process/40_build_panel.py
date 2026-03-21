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
    """篇章级情感数值编码：离散 + 连续。"""
    logger.info("=" * 60)
    logger.info("步骤 2: 篇章级情感数值编码")
    logger.info("=" * 60)

    # --- LLM 投票结果 离散编码 ---
    df['llm_vote_score'] = df['llm_sentiment'].map(SENTIMENT_MAP).fillna(0).astype(int)
    df['is_positive'] = (df['llm_vote_score'] == 1).astype(int)
    df['is_negative'] = (df['llm_vote_score'] == -1).astype(int)
    df['is_neutral'] = (df['llm_vote_score'] == 0).astype(int)

    # --- LLM 投票结果 连续编码 ---
    df['llm_vote_cont'] = df['llm_vote_score'] * df['llm_agreement_rate'].fillna(0)

    # --- LLM 逐模型 离散 + 连续编码 ---
    for short in LLM_MODELS:
        sent_col = f'{short}_sentiment'
        conf_col = f'{short}_sentiment_confidence'
        if sent_col in df.columns:
            df[f'{short}_score'] = df[sent_col].map(SENTIMENT_MAP).fillna(0).astype(int)
            if conf_col in df.columns:
                df[f'{short}_cont'] = df[f'{short}_score'] * df[conf_col].fillna(0)
            else:
                df[f'{short}_cont'] = df[f'{short}_score'].astype(float)

    # --- 词典法 & BERT: 直接使用上游连续值, 无需额外编码 ---

    encoded_cols = ['llm_vote_score', 'is_positive', 'is_negative', 'is_neutral',
                    'llm_vote_cont']
    for short in LLM_MODELS:
        encoded_cols.extend([f'{short}_score', f'{short}_cont'])

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
    """构建 GroupBy 聚合字典。"""
    agg = {}

    # --- A. LLM 逐模型 ---
    for short in LLM_MODELS:
        score_col = f'{short}_score'
        cont_col = f'{short}_cont'
        agg[f'{short}_tone'] = (score_col, 'mean')
        agg[f'{short}_tone_sum'] = (score_col, 'sum')
        agg[f'{short}_cont_mean'] = (cont_col, 'mean')
        agg[f'{short}_cont_sum'] = (cont_col, 'sum')
        agg[f'{short}_tone_std'] = (score_col, 'std')

    # --- B. LLM 投票结果 ---
    agg['llm_vote_tone'] = ('llm_vote_score', 'mean')
    agg['llm_vote_tone_sum'] = ('llm_vote_score', 'sum')
    agg['llm_vote_tone_std'] = ('llm_vote_score', 'std')
    agg['pos_frac'] = ('is_positive', 'mean')
    agg['neg_frac'] = ('is_negative', 'mean')
    agg['pos_count'] = ('is_positive', 'sum')
    agg['neg_count'] = ('is_negative', 'sum')
    agg['llm_vote_cont'] = ('llm_vote_cont', 'mean')
    agg['llm_vote_cont_sum'] = ('llm_vote_cont', 'sum')

    # --- C. 词典法 ---
    for d in DICT_NAMES:
        score_col = f'{d}_score'
        agg[f'{d}_tone'] = (score_col, 'mean')
        agg[f'{d}_tone_sum'] = (score_col, 'sum')
        agg[f'{d}_tone_std'] = (score_col, 'std')

    # --- D. BERT 逐模型 ---
    for short in BERT_MODELS:
        pos_col = f'{short}_正面'
        neg_col = f'{short}_负面'
        agg[f'{short}_pos'] = (pos_col, 'mean')
        agg[f'{short}_pos_sum'] = (pos_col, 'sum')
        agg[f'{short}_neg'] = (neg_col, 'mean')
        agg[f'{short}_neg_sum'] = (neg_col, 'sum')
        agg[f'{short}_pos_std'] = (pos_col, 'std')
        if short in THREE_CLASS_MODELS:
            neu_col = f'{short}_中性'
            agg[f'{short}_neu'] = (neu_col, 'mean')
            agg[f'{short}_neu_sum'] = (neu_col, 'sum')

    # --- E. 新闻覆盖量 & 稳健性辅助 ---
    agg['n_articles'] = ('llm_vote_score', 'count')
    agg['headline_frac'] = ('in_title', 'mean')
    agg['multi_bank_frac'] = ('is_multi_bank', 'mean')
    agg['avg_bank_count'] = ('bank_count', 'mean')
    agg['max_bank_count'] = ('bank_count', 'max')
    agg['avg_agreement_rate'] = ('llm_agreement_rate', 'mean')

    # tech_frac (is_fintech_news 可能不存在)
    # 会在聚合后单独处理

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
    count_cols = ['pos_count', 'neg_count']
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
    llm_tone_cols = [f'{s}_tone' for s in LLM_MODELS]
    llm_tone_sum_cols = [f'{s}_tone_sum' for s in LLM_MODELS]
    llm_cont_cols = [f'{s}_cont_mean' for s in LLM_MODELS]
    llm_cont_sum_cols = [f'{s}_cont_sum' for s in LLM_MODELS]
    llm_std_cols = [f'{s}_tone_std' for s in LLM_MODELS]

    panel['llm_models_avg_tone'] = _safe_mean(llm_tone_cols)
    panel['llm_models_avg_tone_sum'] = _safe_mean(llm_tone_sum_cols)
    panel['llm_models_avg_cont'] = _safe_mean(llm_cont_cols)
    panel['llm_models_avg_cont_sum'] = _safe_mean(llm_cont_sum_cols)
    panel['llm_models_avg_tone_std'] = _safe_mean(llm_std_cols)

    # --- 词典法综合 ---
    dict_tone_cols = [f'{d}_tone' for d in DICT_NAMES]
    dict_tone_sum_cols = [f'{d}_tone_sum' for d in DICT_NAMES]
    dict_std_cols = [f'{d}_tone_std' for d in DICT_NAMES]

    panel['dict_avg_tone'] = _safe_mean(dict_tone_cols)
    panel['dict_avg_tone_sum'] = _safe_mean(dict_tone_sum_cols)
    panel['dict_avg_tone_std'] = _safe_mean(dict_std_cols)

    # --- BERT 综合 ---
    bert_pos_cols = [f'{b}_pos' for b in BERT_MODELS]
    bert_neg_cols = [f'{b}_neg' for b in BERT_MODELS]
    bert_neu_cols = [f'{b}_neu' for b in BERT_MODELS if b in THREE_CLASS_MODELS]
    bert_pos_sum_cols = [f'{b}_pos_sum' for b in BERT_MODELS]
    bert_neg_sum_cols = [f'{b}_neg_sum' for b in BERT_MODELS]
    bert_neu_sum_cols = [f'{b}_neu_sum' for b in BERT_MODELS if b in THREE_CLASS_MODELS]
    bert_pos_std_cols = [f'{b}_pos_std' for b in BERT_MODELS]

    panel['bert_avg_pos'] = _safe_mean(bert_pos_cols)
    panel['bert_avg_neg'] = _safe_mean(bert_neg_cols)
    panel['bert_avg_neu'] = _safe_mean(bert_neu_cols)
    panel['bert_avg_pos_sum'] = _safe_mean(bert_pos_sum_cols)
    panel['bert_avg_neg_sum'] = _safe_mean(bert_neg_sum_cols)
    panel['bert_avg_neu_sum'] = _safe_mean(bert_neu_sum_cols)
    panel['bert_avg_pos_std'] = _safe_mean(bert_pos_std_cols)

    composite_count = 15  # 以上共 15 个综合指标
    logger.info(f"  生成综合指标: {composite_count} 个")
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

    if 'llm_vote_tone' in panel.columns:
        valid_tone = panel['llm_vote_tone'].dropna()
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
    required_cols = ['target_bank', 'llm_sentiment', '日期', 'llm_agreement_rate']
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
