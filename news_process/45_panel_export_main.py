"""
45_panel_export_main.py — 面板导出与主流程编排 (入口文件)
==========================================================

本文件是整个金融科技新闻研究管线的主入口和编排器。

核心功能:
  1. 面板诊断统计 (log_diagnostics): 输出覆盖率、平衡性、缺失值等
  2. 多格式导出 (export_panel): Parquet + Stata .dta (含学术级标签)
  3. 主流程编排 main(): 41→42→43→44→46→47→45 的执行序列

执行序列 (步骤号对应 main() 中的日志标记):
  Step 1-3: 数据加载、情感编码、面板聚合 (41_panel_encode_aggregate)
  Step 4-5: 金融科技注意力 + 媒体异质性 (42_panel_attention_media)
  Step 6:   复合指标 + 地理缓冲 + AI 模仿 (43_panel_indicators_geography)
  Step 7a-e: Bartik IV + DID + 政策冲击 (44_panel_iv_did)
  Step 7f:  同行网络溢出 (46_network_spillovers)
  Step 7g:  网络中心度 22 指标 (46_network_spillovers)
  Step 7h:  经纪网络 + LOO冲击 + 火灾甩卖 (47_network_brokerage)
  Step 8-9: 诊断统计 + 多格式导出 (45_panel_export_main)

拆分自: 40_build_panel.py (L2187-3142)

运行方式:
  python 45_panel_export_main.py
"""

import os
import re
import sys
import json
import time
import importlib.util as _iu

import numpy as np
import pandas as pd

# --- 从 41 导入共享配置和函数 ---
# 41_panel_encode_aggregate.py: 情感编码 + 面板聚合
# 提供: CONFIG(全局配置), encode_sentiment(情感映射),
#   aggregate_panel(银行-年聚合), balance_panel(面板平衡)
_p41 = os.path.join(os.path.dirname(__file__), '41_panel_encode_aggregate.py')
_s41 = _iu.spec_from_file_location('_41_mod', _p41)
_m41 = _iu.module_from_spec(_s41)
_s41.loader.exec_module(_m41)

CONFIG = _m41.CONFIG
STAGE_NAME = _m41.STAGE_NAME
logger = _m41.logger
OUTPUT_DIR = _m41.OUTPUT_DIR
FILENAMES = _m41.FILENAMES
PANEL_CFG = _m41.PANEL_CFG
LLM_MODELS = _m41.LLM_MODELS
DICT_NAMES = _m41.DICT_NAMES
BERT_MODELS = _m41.BERT_MODELS
THREE_CLASS_MODELS = _m41.THREE_CLASS_MODELS
SENTIMENT_MAP = _m41.SENTIMENT_MAP

encode_sentiment = _m41.encode_sentiment
compute_media_authority_weights = _m41.compute_media_authority_weights
parse_time = _m41.parse_time
build_aggregation_dict = _m41.build_aggregation_dict
aggregate_panel = _m41.aggregate_panel
balance_panel = _m41.balance_panel

from utils.helpers import log_stage_summary, save_dataset

# --- 从 42 导入 ---
# 42_panel_attention_media.py: 金融科技注意力指数 + 媒体异质性指标
# 提供: ft_attn_yr/prov/city, 媒体类型占比, 情感缺口, HHI 等
_p42 = os.path.join(os.path.dirname(__file__), '42_panel_attention_media.py')
_s42 = _iu.spec_from_file_location('_42_mod', _p42)
_m42 = _iu.module_from_spec(_s42)
_s42.loader.exec_module(_m42)

compute_fintech_attention_index = _m42.compute_fintech_attention_index
compute_media_heterogeneity = _m42.compute_media_heterogeneity

# --- 从 43 导入 ---
# 43_panel_indicators_geography.py: 复合指标 + 28种地理缓冲 + 6层AI模仿
# 提供: 标准化变量, LOO情感, 银行地理坐标合并等
_p43 = os.path.join(os.path.dirname(__file__), '43_panel_indicators_geography.py')
_s43 = _iu.spec_from_file_location('_43_mod', _p43)
_m43 = _iu.module_from_spec(_s43)
_s43.loader.exec_module(_m43)

compute_composite_indicators = _m43.compute_composite_indicators
standardize_panel_variables = _m43.standardize_panel_variables
merge_bank_geography = _m43.merge_bank_geography
compute_leave_one_out_sentiment = _m43.compute_leave_one_out_sentiment

# --- 从 44 导入 ---
# 44_panel_iv_did.py: Bartik IV + 政策冲击 DID
# 提供: shift-share IV, 地理分区 LOO, 政策事件合并等
_p44 = os.path.join(os.path.dirname(__file__), '44_panel_iv_did.py')
_s44 = _iu.spec_from_file_location('_44_mod', _p44)
_m44 = _iu.module_from_spec(_s44)
_s44.loader.exec_module(_m44)

load_bank_group_maps = _m44.load_bank_group_maps
compute_bartik_iv = _m44.compute_bartik_iv
compute_bartik_iv_fintech = _m44.compute_bartik_iv_fintech
PROVINCE_TO_ZONE = _m44.PROVINCE_TO_ZONE
compute_zone_leave1out = _m44.compute_zone_leave1out
merge_policy_shocks = _m44.merge_policy_shocks

# --- 从 46 导入 (网络溢出) ---
# 46_network_spillovers.py: 同行溢出 + 22种中心度 + 认知邻近度
# 可选依赖: 该文件可能不存在于早期版本, 通过 os.path.exists 守护
_p46 = os.path.join(os.path.dirname(__file__), '46_network_spillovers.py')
if os.path.exists(_p46):
    _s46 = _iu.spec_from_file_location('_46_mod', _p46)
    _m46 = _iu.module_from_spec(_s46)
    _s46.loader.exec_module(_m46)
    compute_network_spillovers = _m46.compute_network_spillovers
    compute_bank_network_centrality = _m46.compute_bank_network_centrality
    compute_cognitive_proximity = getattr(_m46, 'compute_cognitive_proximity', None)
else:
    compute_network_spillovers = None
    compute_bank_network_centrality = None
    compute_cognitive_proximity = None

# --- 从 47 导入 (信息经纪网络) ---
# 47_network_brokerage.py: 媒体-银行二分图中心度 + LOO行业冲击 + 火灾甩卖
# 可选依赖: 同上, 通过 os.path.exists 守护
_p47 = os.path.join(os.path.dirname(__file__), '47_network_brokerage.py')
if os.path.exists(_p47):
    _s47 = _iu.spec_from_file_location('_47_mod', _p47)
    _m47 = _iu.module_from_spec(_s47)
    _s47.loader.exec_module(_m47)
    compute_brokerage_centrality = _m47.compute_brokerage_centrality
    compute_industry_neg_shock = _m47.compute_industry_neg_shock
    compute_fire_sale_interaction = _m47.compute_fire_sale_interaction
else:
    compute_brokerage_centrality = None
    compute_industry_neg_shock = None
    compute_fire_sale_interaction = None


# ============================================================================
# 8. 诊断统计量
# ============================================================================

def log_diagnostics(panel: pd.DataFrame, df_exploded: pd.DataFrame):
    """输出面板诊断统计, 包含分类维度(底层技术/应用场景)的覆盖率、置信度
    和面板平衡性诊断 (G-07)。"""
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
    for suffix, label in [('_tech', '底层技术'), ('_app', '应用场景'), ('_mix', '混合型')]:
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

            # ── G-20: 低置信度分类诊断列 ──
            # 纯诊断性质: 标记 avg_category_confidence < 0.5 的 Bank-Year,
            # 供下游分析筛选, 不改变任何指标的计算逻辑
            panel['low_conf_flag'] = (
                panel['avg_category_confidence'] < 0.5
            ).astype(int)
            low_n = panel['low_conf_flag'].sum()
            low_pct = low_n / max(len(panel), 1)
            logger.info(f"  G-20 低置信度标记: {low_n}/{len(panel)} "
                        f"({low_pct:.1%} Bank-Year, conf < 0.5)")

    # ── G-14: 距离衰减敏感性检验结果摘要 ──
    decay_report = os.path.join(OUTPUT_DIR, 'eval_reports', '38_decay_sensitivity.csv')
    if os.path.exists(decay_report):
        try:
            decay_df = pd.read_csv(decay_report)
            # 计算 uniform vs inverse 的平均 Pearson
            dict_names = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
            pearsons = []
            for dn in dict_names:
                u_col, d_col = f'{dn}_uniform', f'{dn}_inverse'
                if u_col in decay_df.columns and d_col in decay_df.columns:
                    r = decay_df[u_col].corr(decay_df[d_col])
                    if not np.isnan(r):
                        pearsons.append(r)
            if pearsons:
                logger.info(f"  G-14 距离衰减: Pearson(uniform, inverse) = "
                            f"{np.mean(pearsons):.4f} (avg), "
                            f"{min(pearsons):.4f} (min)")
        except Exception as e:
            logger.debug(f"  G-14 报告读取失败: {e}")

    # 文章级统计
    logger.info(f"  展开后文章-银行级行数: {len(df_exploded):,}")
    logger.info(f"  多银行文章占比: {df_exploded['is_multi_bank'].mean():.1%}")


    # ── G-07: 面板平衡性诊断 ──
    # 学术依据: Wooldridge (2010), Baltagi (2021) — 不平衡面板的标准诊断
    logger.info("")
    logger.info("  --- 面板平衡性诊断 (G-07) ---")

    # (a) 理论最大行数 vs 实际行数
    max_years = year_max - year_min + 1
    theoretical_rows = n_banks * max_years
    balance_ratio = len(panel) / theoretical_rows if theoretical_rows > 0 else 0
    logger.info(f"  理论最大维度: {n_banks} 银行 × {max_years} 年 = {theoretical_rows:,} 行")
    logger.info(f"  实际行数: {len(panel):,} ({balance_ratio:.1%} 平衡率)")
    if balance_ratio >= 0.95:
        logger.info(f"  ✅ 高度平衡面板 (≥95%)")
    elif balance_ratio >= 0.80:
        logger.info(f"  ⚠️ 近似平衡面板 (80-95%)")
    else:
        logger.info(f"  🔴 不平衡面板 (<80%), 建议检查银行进入/退出")

    # (b) 每家银行的年份覆盖
    bank_year_counts = panel.groupby('target_bank')['year'].nunique()
    full_coverage = (bank_year_counts == max_years).sum()
    partial = (bank_year_counts < max_years).sum()
    logger.info(f"  完整覆盖 ({max_years} 年): {full_coverage}/{n_banks} 银行 "
                f"({full_coverage/n_banks:.1%})")
    if partial > 0:
        min_years = bank_year_counts.min()
        logger.info(f"  部分覆盖银行: {partial} 家, 最少仅覆盖 {min_years} 年")

    # (c) 每年的银行数
    year_bank_counts = panel.groupby('year')['target_bank'].nunique()
    logger.info(f"  逐年银行数分布:")
    for yr in sorted(year_bank_counts.index):
        cnt = year_bank_counts[yr]
        marker = "" if cnt == n_banks else f" (缺 {n_banks - cnt})"
        logger.info(f"    {yr}: {cnt} 家{marker}")

    # (d) 有效覆盖率 (有新闻的 Bank-Year 占比)
    has_news = (panel['n_articles'] > 0).sum()
    news_coverage = has_news / len(panel) if len(panel) > 0 else 0
    logger.info(f"  有效新闻覆盖: {has_news}/{len(panel)} Bank-Year ({news_coverage:.1%})")

    # (e) 关键变量缺失率
    key_vars = ['llm_vote_tone_full', 'llm_vote_tone_ctx', 'bank_province',
                'bank_city', 'ln_news_coverage']
    logger.info(f"  关键变量缺失率:")
    for var in key_vars:
        if var in panel.columns:
            miss = panel[var].isna().sum()
            miss_pct = miss / len(panel) if len(panel) > 0 else 0
            logger.info(f"    {var}: {miss:,}/{len(panel):,} ({miss_pct:.1%})")


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
                # 注意力指数 (Da et al. 2011; Fang & Peress 2009)
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
                # 媒体异质性 - 占比 (新增四维度)
                'official_media_frac':          'Official Media Share (You 2018)',
                'market_media_frac':            'Market Media Share (You 2018)',
                'deepdive_media_frac':          'Deep-dive Periodical Share (Bushee 2010)',
                'daily_media_frac':             'High-freq Daily Share (Tetlock 2007)',
                # 媒体异质性 - 新增情感均值 (Full 轨道)
                'tone_official_media_full':     'Avg Tone: Official Media (Full)',
                'tone_nonoff_media_full':       'Avg Tone: Non-Official Media (Full)',
                'tone_market_media_full':       'Avg Tone: Market Media (Full)',
                'tone_nonmkt_media_full':       'Avg Tone: Non-Market Media (Full)',
                'tone_deepdive_media_full':     'Avg Tone: Deep-dive Media (Full)',
                'tone_nondeep_media_full':      'Avg Tone: Non-Deep Media (Full)',
                'tone_daily_media_full':        'Avg Tone: Daily Media (Full)',
                'tone_nondaily_media_full':     'Avg Tone: Non-Daily Media (Full)',
                # 媒体异质性 - 新增情感均值 (Ctx 轨道)
                'tone_official_media_ctx':      'Avg Tone: Official Media (Ctx)',
                'tone_nonoff_media_ctx':        'Avg Tone: Non-Official Media (Ctx)',
                'tone_market_media_ctx':        'Avg Tone: Market Media (Ctx)',
                'tone_nonmkt_media_ctx':        'Avg Tone: Non-Market Media (Ctx)',
                'tone_deepdive_media_ctx':      'Avg Tone: Deep-dive Media (Ctx)',
                'tone_nondeep_media_ctx':       'Avg Tone: Non-Deep Media (Ctx)',
                'tone_daily_media_ctx':         'Avg Tone: Daily Media (Ctx)',
                'tone_nondaily_media_ctx':      'Avg Tone: Non-Daily Media (Ctx)',
                # 媒体异质性 - 新增情感缺口 (Full)
                'tone_gap_official_nonoff_full':   'Tone Gap: Official-NonOff (Full)',
                'tone_gap_market_nonmkt_full':     'Tone Gap: Market-NonMkt (Full)',
                'tone_gap_deepdive_nondeep_full':  'Tone Gap: DeepDive-NonDeep (Full)',
                'tone_gap_daily_nondaily_full':    'Tone Gap: Daily-NonDaily (Full)',
                # 媒体异质性 - 新增情感缺口 (Ctx)
                'tone_gap_official_nonoff_ctx':    'Tone Gap: Official-NonOff (Ctx)',
                'tone_gap_market_nonmkt_ctx':      'Tone Gap: Market-NonMkt (Ctx)',
                'tone_gap_deepdive_nondeep_ctx':   'Tone Gap: DeepDive-NonDeep (Ctx)',
                'tone_gap_daily_nondaily_ctx':     'Tone Gap: Daily-NonDaily (Ctx)',
                # 集中度
                'media_hhi':                   'Media Source HHI',
                # 媒体权威性加权 (Holzman et al. 2023, TAR)
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
                # 银行注册地地理信息 (Luo & Li 2025, FRL, Table A.2)
                # 用途: vce(cluster bank_province), vce(cluster bank_city)
                'bank_province':                   'Bank HQ Province (Registration)',
                'bank_city':                       'Bank HQ City (Registration)',
                # Leave-one-out 地理平均情感 IV (Luo & Li 2025, Table 3)
                # 定义: 同省/同城市其他银行的年度平均情感 (排除自身)
                # 用途: ivreghdfe Y (tone = prov_leave1out_tone_full) X, ...
                'prov_leave1out_tone_full':         'Province Leave-1-Out Tone (Full)',
                'prov_leave1out_tone_ctx':          'Province Leave-1-Out Tone (Ctx)',
                'city_leave1out_tone_full':         'City Leave-1-Out Tone (Full)',
                'city_leave1out_tone_ctx':          'City Leave-1-Out Tone (Ctx)',
                # Bartik IV — 银行类型维度 (主)
                'bank_type':                           'Bank Type (nfra_type)',
                'bartik_type_iv_full':                 'Bartik IV: Bank-Type (Full)',
                'bartik_type_iv_ctx':                  'Bartik IV: Bank-Type (Ctx)',
                'bartik_type_share_soe':               'Bartik Share: SOE Banks',
                'bartik_type_share_joint':             'Bartik Share: Joint-Stock',
                'bartik_type_share_city':              'Bartik Share: City Commercial',
                'bartik_type_share_rural':             'Bartik Share: Rural Commercial',
                'bartik_type_share_private':           'Bartik Share: Private Banks',
                'bartik_type_share_foreign':           'Bartik Share: Foreign Banks',
                # Bartik IV — 规模维度 (稳健性 1)
                'bank_scale':                          'Bank Scale (enterprise_scale)',
                'bartik_scale_iv_full':                'Bartik IV: Bank-Scale (Full)',
                'bartik_scale_iv_ctx':                 'Bartik IV: Bank-Scale (Ctx)',
                'bartik_scale_share_L':                'Bartik Share: Large Banks',
                'bartik_scale_share_M':                'Bartik Share: Medium Banks',
                'bartik_scale_share_S':                'Bartik Share: Small Banks',
                'bartik_scale_share_XS':               'Bartik Share: Micro Banks',
                # Bartik IV — 金融科技类型维度 (稳健性 2)
                'bartik_fintech_iv_full':              'Bartik IV: Fintech-Category (Full)',
                'bartik_fintech_iv_ctx':               'Bartik IV: Fintech-Category (Ctx)',
                'bartik_fintech_share_tech':           'Bartik Share: Technology',
                'bartik_fintech_share_app':            'Bartik Share: Application',
                # Bartik IV — 媒体类型维度 (稳健性 3)
                'bartik_media_iv_full':                'Bartik IV: Media-Type (Full)',
                'bartik_media_iv_ctx':                 'Bartik IV: Media-Type (Ctx)',
                'bartik_media_share_fin':              'Bartik Share: Financial Media',
                'bartik_media_share_comp':             'Bartik Share: Comprehensive Media',
                # Bartik IV — 中央/地方 (稳健性 4)
                'bartik_mcentral_iv_full':             'Bartik IV: Central-Local (Full)',
                'bartik_mcentral_iv_ctx':              'Bartik IV: Central-Local (Ctx)',
                'bartik_mcentral_share_central':       'Bartik Share: Central Media',
                'bartik_mcentral_share_local':         'Bartik Share: Local Media',
                # Bartik IV — 财经/非财经 (稳健性 5)
                'bartik_mfin_iv_full':                 'Bartik IV: Fin-NonFin (Full)',
                'bartik_mfin_iv_ctx':                  'Bartik IV: Fin-NonFin (Ctx)',
                'bartik_mfin_share_fin':               'Bartik Share: Financial',
                'bartik_mfin_share_nonfin':            'Bartik Share: Non-Financial',
                # Bartik IV — 综合类/非综合类 (稳健性 6)
                'bartik_mcomp_iv_full':                'Bartik IV: Comp-NonComp (Full)',
                'bartik_mcomp_iv_ctx':                 'Bartik IV: Comp-NonComp (Ctx)',
                'bartik_mcomp_share_comp':             'Bartik Share: Comprehensive',
                'bartik_mcomp_share_noncomp':          'Bartik Share: Non-Comprehensive',
                # Bartik IV — 官方/非官方 (稳健性 7a)
                'bartik_mofficial_iv_full':             'Bartik IV: Official-NonOff (Full)',
                'bartik_mofficial_iv_ctx':              'Bartik IV: Official-NonOff (Ctx)',
                'bartik_mofficial_share_official':      'Bartik Share: Official Media',
                'bartik_mofficial_share_nonoff':        'Bartik Share: Non-Official',
                # Bartik IV — 市场化/非市场化 (稳健性 7b)
                'bartik_mmarket_iv_full':               'Bartik IV: Market-NonMkt (Full)',
                'bartik_mmarket_iv_ctx':                'Bartik IV: Market-NonMkt (Ctx)',
                'bartik_mmarket_share_market':          'Bartik Share: Market Media',
                'bartik_mmarket_share_nonmkt':          'Bartik Share: Non-Market',
                # Bartik IV — 出版频率三方 (稳健性 7c)
                'bartik_mfreq_iv_full':                'Bartik IV: Pub-Frequency (Full)',
                'bartik_mfreq_iv_ctx':                 'Bartik IV: Pub-Frequency (Ctx)',
                'bartik_mfreq_share_deepdive':          'Bartik Share: Deep-dive',
                'bartik_mfreq_share_daily':             'Bartik Share: Daily',
                # Bartik IV — 深度/非深度 (稳健性 7d)
                'bartik_mdeep_iv_full':                'Bartik IV: Deep-NonDeep (Full)',
                'bartik_mdeep_iv_ctx':                 'Bartik IV: Deep-NonDeep (Ctx)',
                'bartik_mdeep_share_deepdive':          'Bartik Share: Deep-dive',
                'bartik_mdeep_share_nondeep':           'Bartik Share: Non-Deep',
                # Bartik IV — 日报/非日报 (稳健性 7e)
                'bartik_mdaily_iv_full':                'Bartik IV: Daily-NonDaily (Full)',
                'bartik_mdaily_iv_ctx':                 'Bartik IV: Daily-NonDaily (Ctx)',
                'bartik_mdaily_share_daily':            'Bartik Share: Daily',
                'bartik_mdaily_share_nondaily':         'Bartik Share: Non-Daily',
                # Bartik IV — 媒体省份 (稳健性 8)
                'bartik_mprov_iv_full':                'Bartik IV: Media-Province (Full)',
                'bartik_mprov_iv_ctx':                 'Bartik IV: Media-Province (Ctx)',
                # Bartik IV — 媒体权威性 (稳健性 8)
                'bartik_mauth_iv_full':                'Bartik IV: Media-Authority (Full)',
                'bartik_mauth_iv_ctx':                 'Bartik IV: Media-Authority (Ctx)',
                'bartik_mauth_share_high':             'Bartik Share: High Authority',
                'bartik_mauth_share_mid':              'Bartik Share: Mid Authority',
                'bartik_mauth_share_low':              'Bartik Share: Low Authority',
                # Bartik IV — 文章长度 (稳健性 9)
                'bartik_doclen_iv_full':               'Bartik IV: Doc-Length (Full)',
                'bartik_doclen_iv_ctx':                'Bartik IV: Doc-Length (Ctx)',
                'bartik_doclen_share_long':            'Bartik Share: Long Articles',
                'bartik_doclen_share_short':           'Bartik Share: Short Articles',
                # Bartik IV — 半年度 (稳健性 10)
                'bartik_half_iv_full':                 'Bartik IV: Half-Year (Full)',
                'bartik_half_iv_ctx':                  'Bartik IV: Half-Year (Ctx)',
                'bartik_half_share_H1':                'Bartik Share: First Half',
                'bartik_half_share_H2':                'Bartik Share: Second Half',
                # Bartik IV — 季度 (稳健性 11)
                'bartik_qtr_iv_full':                  'Bartik IV: Quarter (Full)',
                'bartik_qtr_iv_ctx':                   'Bartik IV: Quarter (Ctx)',
                # Bartik IV — 月度 (稳健性 12)
                'bartik_month_iv_full':                'Bartik IV: Month (Full)',
                'bartik_month_iv_ctx':                 'Bartik IV: Month (Ctx)',
                # Bartik IV — 工作日/周末 (稳健性 13)
                'bartik_wkday_iv_full':                'Bartik IV: Weekday-Weekend (Full)',
                'bartik_wkday_iv_ctx':                 'Bartik IV: Weekday-Weekend (Ctx)',
                # Bartik IV — 专属/共享 (稳健性 14)
                'bartik_excl_iv_full':                 'Bartik IV: Exclusive-Shared (Full)',
                'bartik_excl_iv_ctx':                  'Bartik IV: Exclusive-Shared (Ctx)',
                'bartik_excl_share_exclusive':         'Bartik Share: Exclusive',
                'bartik_excl_share_shared':            'Bartik Share: Shared',
                # Bartik IV — 地理邻近 (稳健性 15)
                'bartik_geoprox_iv_full':              'Bartik IV: Geo-Proximity (Full)',
                'bartik_geoprox_iv_ctx':               'Bartik IV: Geo-Proximity (Ctx)',
                # Bartik IV — 标题出现 (稳健性 16)
                'bartik_title_iv_full':                'Bartik IV: Title-Body (Full)',
                'bartik_title_iv_ctx':                 'Bartik IV: Title-Body (Ctx)',
                # Bartik IV — 关键词多样性 (稳健性 17)
                'bartik_mden_iv_full':                 'Bartik IV: Mention-Density (Full)',
                'bartik_mden_iv_ctx':                  'Bartik IV: Mention-Density (Ctx)',
                # Bartik IV — 关键词密度 (稳健性 18)
                'bartik_mcount_iv_full':               'Bartik IV: Mention-Count (Full)',
                'bartik_mcount_iv_ctx':                'Bartik IV: Mention-Count (Ctx)',
                # Bartik IV — 提及密度 (稳健性 19)
                'bartik_breadth_iv_full':              'Bartik IV: Outlet-Breadth (Full)',
                'bartik_breadth_iv_ctx':               'Bartik IV: Outlet-Breadth (Ctx)',
                # Bartik IV — 银行提及次数 (稳健性 20)
                'bartik_fwdlook_iv_full':              'Bartik IV: Forward-Looking (Full)',
                'bartik_fwdlook_iv_ctx':               'Bartik IV: Forward-Looking (Ctx)',
                # Bartik IV — 媒体覆盖广度 (稳健性 21)
                'bartik_sentlen_iv_full':              'Bartik IV: Sentence-Length (Full)',
                'bartik_sentlen_iv_ctx':               'Bartik IV: Sentence-Length (Ctx)',
                # Bartik IV — 前瞻性语言 (稳健性 22)
                'bartik_ttr_iv_full':                  'Bartik IV: Type-Token-Ratio (Full)',
                'bartik_ttr_iv_ctx':                   'Bartik IV: Type-Token-Ratio (Ctx)',
                # Bartik IV — 平均句长 (稳健性 23)
                'bartik_pubfmt_iv_full':               'Bartik IV: Pub-Format (Full)',
                'bartik_pubfmt_iv_ctx':                'Bartik IV: Pub-Format (Ctx)',
                # Bartik IV — 词汇丰富度 (稳健性 24)
                'bartik_author_iv_full':               'Bartik IV: Author-Byline (Full)',
                'bartik_author_iv_ctx':                'Bartik IV: Author-Byline (Ctx)',
                # Bartik IV — 出版形态 (稳健性 25)
                'bartik_page_iv_full':                 'Bartik IV: Section-Position (Full)',
                'bartik_page_iv_ctx':                  'Bartik IV: Section-Position (Ctx)',
                # Bartik IV — 作者署名 (稳健性 26)
                'bartik_pgnum_iv_full':                'Bartik IV: Page-Number (Full)',
                'bartik_pgnum_iv_ctx':                 'Bartik IV: Page-Number (Ctx)',
                # Bartik IV — 版面位置 (稳健性 27)
                'bartik_kwdiv_iv_full':                'Bartik IV: Keyword-Diversity (Full)',
                'bartik_kwdiv_iv_ctx':                 'Bartik IV: Keyword-Diversity (Ctx)',
                # Bartik IV — 页号位置 (稳健性 28)
                'bartik_kwden_iv_full':                'Bartik IV: Keyword-Density (Full)',
                'bartik_kwden_iv_ctx':                 'Bartik IV: Keyword-Density (Ctx)',
                # Bartik IV — 基期敏感性
                'bartik_type_iv_full_t0':              'Bartik IV: Type (Full, T0)',
                'bartik_type_iv_full_t1':              'Bartik IV: Type (Full, T0+1)',
                'bartik_type_iv_full_t01':             'Bartik IV: Type (Full, T0&T0+1)',
                'bartik_type_iv_ctx_t0':               'Bartik IV: Type (Ctx, T0)',
                'bartik_type_iv_ctx_t1':               'Bartik IV: Type (Ctx, T0+1)',
                'bartik_type_iv_ctx_t01':              'Bartik IV: Type (Ctx, T0&T0+1)',
                # 经济圈 LOO IV
                'zone_leave1out_tone_full':            'Econ Zone Leave-1-Out Tone (Full)',
                'zone_leave1out_tone_ctx':             'Econ Zone Leave-1-Out Tone (Ctx)',
                'bank_zone':                           'Economic Zone',
                # DID 政策冲击
                'dcep_treated':                        'DCEP Pilot (0/1)',
                'dcep_post':                           'Post DCEP Pilot (0/1)',
                'dcep_treat_year':                     'DCEP First Treatment Year',
                'sandbox_treated':                     'Fintech Sandbox (0/1)',
                'sandbox_post':                        'Post Sandbox (0/1)',
                'sandbox_treat_year':                  'Sandbox First Treatment Year',
                # Event Study 动态效应 (Callaway & Sant'Anna 2021, JoE)
                'dcep_rel_year':                       'DCEP Relative Year to Treatment',
                'dcep_lead3':                          'DCEP Lead 3 Periods (k=-3)',
                'dcep_lead2':                          'DCEP Lead 2 Periods (k=-2)',
                'dcep_lag0':                           'DCEP Treatment Year (k=0)',
                'dcep_lag1':                           'DCEP Lag 1 Period (k=+1)',
                'dcep_lag2':                           'DCEP Lag 2 Periods (k=+2)',
                'dcep_lag3':                           'DCEP Lag 3 Periods (k=+3)',
                'dcep_lead4plus':                      'DCEP Lead 4+ Periods (k<=-4)',
                'dcep_lag4plus':                       'DCEP Lag 4+ Periods (k>=+4)',
                'sandbox_rel_year':                    'Sandbox Relative Year to Treatment',
                'sandbox_lead3':                       'Sandbox Lead 3 Periods (k=-3)',
                'sandbox_lead2':                       'Sandbox Lead 2 Periods (k=-2)',
                'sandbox_lag0':                        'Sandbox Treatment Year (k=0)',
                'sandbox_lag1':                        'Sandbox Lag 1 Period (k=+1)',
                'sandbox_lag2':                        'Sandbox Lag 2 Periods (k=+2)',
                'sandbox_lag3':                        'Sandbox Lag 3 Periods (k=+3)',
                'sandbox_lead4plus':                   'Sandbox Lead 4+ Periods (k<=-4)',
                'sandbox_lag4plus':                    'Sandbox Lag 4+ Periods (k>=+4)',
                # LLM 置信度 (Shapiro et al. 2022, JoE; Baker et al. 2024, JAR)
                'avg_llm_conf_full':                   'LLM Avg Confidence (Full)',
                'avg_llm_conf_std_full':               'LLM Confidence Std Dev (Full)',
                'avg_llm_conf_ctx':                    'LLM Avg Confidence (Ctx)',
                'avg_llm_conf_std_ctx':                'LLM Confidence Std Dev (Ctx)',
                'avg_gpt5nano_conf_full':              'GPT-5nano Confidence (Full)',
                'avg_gpt5nano_conf_ctx':               'GPT-5nano Confidence (Ctx)',
                'avg_gemini3_conf_full':               'Gemini-3 Confidence (Full)',
                'avg_gemini3_conf_ctx':                'Gemini-3 Confidence (Ctx)',
                'avg_claude4h_conf_full':              'Claude-4h Confidence (Full)',
                'avg_claude4h_conf_ctx':               'Claude-4h Confidence (Ctx)',
                # 其他
                'has_coverage':                        'Has News Coverage (0/1)',
                # ═══ 异质性分析变量 (Angrist & Pischke 2009; Brambor et al. 2006) ═══
                'is_soe':                              'SOE Dummy (0/1)',
                'bank_scale_ord':                      'Bank Scale Ordinal (XS=1..L=4)',
                'high_coverage':                       'High Media Coverage (0/1)',
                'tone_x_soe_full':                     'Tone x SOE (Full)',
                'tone_x_soe_ctx':                      'Tone x SOE (Ctx)',
                'tone_x_scale_full':                   'Tone x Bank Scale (Full)',
                'tone_x_scale_ctx':                    'Tone x Bank Scale (Ctx)',
                'tone_x_highcov_full':                 'Tone x High Coverage (Full)',
                'tone_x_highcov_ctx':                  'Tone x High Coverage (Ctx)',
                'digital_frontier':                    'Digital Frontier (0/1)',
                'dcep_ddd_digfront':                   'DCEP x Post x DigFrontier (DDD)',
                'sandbox_ddd_digfront':                'Sandbox x Post x DigFrontier (DDD)',
                'avg_llm_conf_full_z':                 'LLM Confidence Z (Full)',
                'avg_llm_conf_ctx_z':                  'LLM Confidence Z (Ctx)',
                'stress_period':                       'Stress Period (2015/2018/2020)',
                'tone_x_stress_full':                  'Tone x Stress Period (Full)',
                'tone_x_stress_ctx':                   'Tone x Stress Period (Ctx)',
                'depins_post':                         'Post Deposit Insurance (0/1)',
                'tone_x_depins_full':                  'Tone x Deposit Insurance (Full)',
                'tone_x_depins_ctx':                   'Tone x Deposit Insurance (Ctx)',
                'concern_score_full':                  'Concern Score (Full)',
                'concern_score_ctx':                   'Concern Score (Ctx)',
                'llm_vote_tone_full_lag1':             'Lagged Tone t-1 (Full)',
                'llm_vote_tone_ctx_lag1':              'Lagged Tone t-1 (Ctx)',
                'tone_reversal_full':                  'Tone Reversal t-(t-1) (Full)',
                'tone_reversal_ctx':                   'Tone Reversal t-(t-1) (Ctx)',
                # 跟风新闻检测 (Tetlock 2011, JF)
                'avg_herd_weight':                     'Avg Herd Decay Weight 1/(1+N) (Tetlock 2011)',
                'min_herd_weight':                     'Min Herd Decay Weight (Tetlock 2011)',
                # 跟风衰减加权情感 (Tetlock 2011, JF)
                'llm_vote_tone_hw_full':               'LLM Vote Tone (Herd-Decay Wt, Full)',
                'llm_vote_tone_hw_ctx':                'LLM Vote Tone (Herd-Decay Wt, Ctx)',
                'llm_vote_cont_hw_full':               'LLM Vote Cont (Herd-Decay Wt, Full)',
                'llm_vote_cont_hw_ctx':                'LLM Vote Cont (Herd-Decay Wt, Ctx)',
                # ═══ 银行共现网络: Part A (11) ═══
                'bank_degree_cent':     'Co-mention Degree Centrality (Freeman 1979)',
                'bank_strength_cent':   'Co-mention Strength Centrality (Opsahl 2010)',
                'bank_between_cent':    'Co-mention Betweenness (Battiston 2012)',
                'bank_harmonic_cent':   'Co-mention Harmonic Centrality (Boldi 2014)',
                'bank_eigen_cent':      'Co-mention Eigenvec Centrality (Bonacich 1972)',
                'bank_katz_cent':       'Co-mention Katz Centrality (Acemoglu 2012)',
                'bank_subgraph_cent':   'Co-mention Subgraph Centrality (Estrada 2005)',
                'bank_cfbetween_cent':  'Co-mention Current-Flow Betw (Newman 2005)',
                'bank_clustering':      'Co-mention Clustering Coeff (Watts 1998)',
                'bank_constraint':      'Co-mention Structural Constraint (Burt 1992)',
                'bank_is_hub':          'Co-mention Hub (Top 10% Degree, 0/1)',
                # ═══ 银行共现网络: Part B (7) ═══
                'bank_ego_density':     'Co-mention Ego-Network Density (Burt 1992)',
                'bank_ci':              'Co-mention Struct Hole Richness CI (Burt 1992)',
                'bank_effective_size':  'Co-mention Effective Size (Burt 1992)',
                'bank_closeness_cent':  'Co-mention Closeness Centrality (Freeman 1979)',
                'bank_eccentricity':    'Co-mention Eccentricity (Harary 1969)',
                'bank_avg_nbr_deg':     'Co-mention Avg Neighbor Degree (Barrat 2004)',
                'bank_coreness':        'Co-mention K-Core Number (Seidman 1983)',
                # ═══ 银行共现网络: Part C (4) ═══
                'net_density_yr':       'Annual Co-mention Network Density',
                'net_avg_cluster_yr':   'Annual Avg Clustering Coefficient',
                'net_avg_path_yr':      'Annual Avg Path Length (LCC)',
                'net_degree_gini_yr':   'Annual Degree Distribution Gini',
                # ═══ 银行共现网络: Part D (3) ═══
                'peer_tone_2nd_lag1_full':  '2nd-Order Peer Sentiment Spillover (Full)',
                'peer_tone_2nd_lag1_ctx':   '2nd-Order Peer Sentiment Spillover (Ctx)',
                'peer_tone_2nd_lag1_title': '2nd-Order Peer Sentiment Spillover (Title)',
                # ═══ 地理邻近性: 维度⑨ (Gurun & Butler 2012, JF) ═══
                'homeprov_media_frac':              'Home-Province Media Fraction',
                'homecity_media_frac':              'Home-City Media Fraction',
                'tone_homeprov_media_full':         'Home-Province Media Tone (Full)',
                'tone_nonprov_media_full':          'Non-Province Media Tone (Full)',
                'tone_gap_homeprov_nonprov_full':   'Local Media Slant: Prov (Full)',
                'tone_homecity_media_full':         'Home-City Media Tone (Full)',
                'tone_noncity_media_full':          'Non-City Media Tone (Full)',
                'tone_gap_homecity_noncity_full':   'Local Media Slant: City (Full)',
                'neg_frac_homeprov_full':           'Home-Province Neg Frac (Full)',
                'neg_frac_nonprov_full':            'Non-Province Neg Frac (Full)',
                'neg_frac_homecity_full':           'Home-City Neg Frac (Full)',
                'neg_frac_noncity_full':            'Non-City Neg Frac (Full)',
                # 姜富伟系数 (Jiang et al. 2019)
                'jf_coefficient_full':              'JF Coefficient (Full-text)',
                'jf_coefficient_ctx':               'JF Coefficient (Context)',
                'jf_coefficient_title':             'JF Coefficient (Title)',
                # 媒体质量指标 — 洗稿率 44 种 (Bingler et al. 2022, FRL)
                'washing_ratio':                    'Washing Ratio: LLM Vote (Full)',
                'washing_ratio_ctx':                'Washing Ratio: LLM Vote (Ctx)',
                'neg_sub_ratio_full':               'Neg Substantive Ratio (Full)',
                'neg_sub_ratio_ctx':                'Neg Substantive Ratio (Ctx)',
                'washing_asymmetry_full':           'Washing Asymmetry (Full)',
                'washing_asymmetry_ctx':            'Washing Asymmetry (Ctx)',
                'tone_gap_desc_sub_full':           'Tone Gap: Desc-Sub (Full)',
                'tone_gap_desc_sub_ctx':            'Tone Gap: Desc-Sub (Ctx)',
                'washing_ratio_dict':               'WR: Dict 5-Avg (Full)',
                'washing_ratio_dict_ctx':           'WR: Dict 5-Avg (Ctx)',
                'washing_ratio_bert':               'WR: BERT 5-Avg (Full)',
                'washing_ratio_bert_ctx':           'WR: BERT 5-Avg (Ctx)',
                'washing_ratio_hc':                 'WR: Hi-Conf (Full)',
                'washing_ratio_hc_ctx':             'WR: Hi-Conf (Ctx)',
                'washing_tone_shift_full':          'Desc Tone Shift (Full)',
                'washing_tone_shift_ctx':           'Desc Tone Shift (Ctx)',
                'washing_ratio_fl':                 'WR: Fwd-Look (Full)',
                'washing_ratio_fl_ctx':             'WR: Fwd-Look (Ctx)',
                'pos_desc_count_full':              'Pos & Desc Count (Full)',
                'pos_desc_count_ctx':               'Pos & Desc Count (Ctx)',
                'dummy_no_positive_news':           'No Positive News Dummy',
                'low_conf_flag':                    'Low Confidence Flag',
                # 单模型洗稿率 — 双轨 (动态生成)
                **{f'washing_ratio_{m}{s}': f'WR: {m} ({t})'
                   for m in ['gpt5nano', 'gemini3', 'claude4h',
                             'jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018',
                             'finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']
                   for s, t in [('', 'Full'), ('_ctx', 'Ctx')]},
                # ═══ 停刊稳健性 (Heese et al. 2022, JFE) ═══
                'ceased_media_frac':             'Ceased Media Article Share',
                'n_articles_exc':                'N Articles Excl Ceased Media',
                'exc_tone_full':                 'Tone Excl Ceased (LLM Vote, Full)',
                'exc_tone_ctx':                  'Tone Excl Ceased (LLM Vote, Ctx)',
                'exc_tone_title':                'Tone Excl Ceased (LLM Vote, Title)',
                # ═══ 平衡媒体面板 (Wooldridge 2010, §19.9) ═══
                'bal_w0724_tone_full':           'Balanced W07-24 Tone (Full)',
                'bal_w0724_tone_ctx':            'Balanced W07-24 Tone (Ctx)',
                'bal_w0724_tone_title':          'Balanced W07-24 Tone (Title)',
                'bal_w1024_tone_full':           'Balanced W10-24 Tone (Full)',
                'bal_w1024_tone_ctx':            'Balanced W10-24 Tone (Ctx)',
                'bal_w1024_tone_title':          'Balanced W10-24 Tone (Title)',
                'bal_w1124_tone_full':           'Balanced W11-24 Tone (Full)',
                'bal_w1124_tone_ctx':            'Balanced W11-24 Tone (Ctx)',
                'bal_w1124_tone_title':          'Balanced W11-24 Tone (Title)',
                'n_media_bal_w0724':             'N Media Balanced W07-24',
                'n_media_bal_w1024':             'N Media Balanced W10-24',
                'n_media_bal_w1124':             'N Media Balanced W11-24',
                # === 四梯度距离缓冲 (Gurun & Butler 2012) ===
                'prox_50km_n_media':             'N Media Within 50km',
                'prox_50km_n_articles':          'N Articles Within 50km',
                'prox_50km_frac':                'Frac Articles Within 50km',
                'prox_50km_tone_full':           'Avg Tone Within 50km (Full)',
                'prox_50km_pos_frac':            'Pos Frac Within 50km',
                'prox_50km_neg_frac':            'Neg Frac Within 50km',
                'prox_50km_is_local':            'Has Local Media 50km (0/1)',
                'prox_100km_n_media':            'N Media Within 100km',
                'prox_100km_n_articles':         'N Articles Within 100km',
                'prox_100km_frac':               'Frac Articles Within 100km',
                'prox_100km_tone_full':          'Avg Tone Within 100km (Full)',
                'prox_100km_pos_frac':           'Pos Frac Within 100km',
                'prox_100km_neg_frac':           'Neg Frac Within 100km',
                'prox_100km_is_local':           'Has Local Media 100km (0/1)',
                'prox_150km_n_media':            'N Media Within 150km',
                'prox_150km_n_articles':         'N Articles Within 150km',
                'prox_150km_frac':               'Frac Articles Within 150km',
                'prox_150km_tone_full':          'Avg Tone Within 150km (Full)',
                'prox_150km_pos_frac':           'Pos Frac Within 150km',
                'prox_150km_neg_frac':           'Neg Frac Within 150km',
                'prox_150km_is_local':           'Has Local Media 150km (0/1)',
                'prox_200km_n_media':            'N Media Within 200km',
                'prox_200km_n_articles':         'N Articles Within 200km',
                'prox_200km_frac':               'Frac Articles Within 200km',
                'prox_200km_tone_full':          'Avg Tone Within 200km (Full)',
                'prox_200km_pos_frac':           'Pos Frac Within 200km',
                'prox_200km_neg_frac':           'Neg Frac Within 200km',
                'prox_200km_is_local':           'Has Local Media 200km (0/1)',
                # === 区域 AI 模仿渗透率 (Leary & Roberts 2014) ===
                'ai_reg_province':               'AI Imitation Rate (Province)',
                'ai_reg_city':                   'AI Imitation Rate (City)',
                'ai_reg_50km':                   'AI Imitation Rate (50km)',
                'ai_reg_100km':                  'AI Imitation Rate (100km)',
                'ai_reg_150km':                  'AI Imitation Rate (150km)',
                'ai_reg_200km':                  'AI Imitation Rate (200km)',
                # === 认知邻近度 (Boschma 2005) ===
                'bank_cogn_mean':                'Cognitive Proximity (TF-IDF)',
                # === 信息经纪网络 (Han et al. 2024) ===
                'brokerage_eigen_cent':          'Brokerage Eigenvector Cent',
                'industry_neg_shock':            'Industry Neg Shock (LOO)',
                'brokerage_fire_sale':           'Brokerage x Neg Shock',
                # === 同行金融科技溢出 (Berger et al. 2022) ===
                'peer_fintech_exposure_lag1':    'Peer Fintech Exposure (L1)',
                # ═══ 治理约束型合约 (Zhou et al., 2026, JBR §2.1; Core et al. 2003) ═══
                'GOV_equity_ratio':             'Equity Comp / Total Comp Ratio',
                'GOV_cash_ratio':               'Cash Comp / Total Comp Ratio',
                'GOV_top3_pay_gap':             'ln(Top3 Exec Pay / Avg Emp Pay)',
                'GOV_esg_kpi':                  'ESG-KPI in Exec Comp (0/1)',
                'GOV_board_indep':              'Independent Director Ratio',
                'GOV_dual_chair':               'CEO-Chair Duality (0/1)',
                'GOV_comp_committee':           'Compensation Committee (0/1)',
                'GOV_ceo_tenure':               'CEO Tenure (Years)',
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
    """45_panel_export_main 主流程。"""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===    45_panel_export_main: Bank-Year 面板数据构建    ===")
    logger.info("=" * 70)

    # --- 1. 数据加载与验证 ---
    logger.info("=" * 60)
    logger.info("步骤 1: 数据加载与验证")
    logger.info("=" * 60)

    input_filename = FILENAMES.get('output_24_herd_decay', '24_herd_decay.parquet')
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
        for track in ['_full', '_ctx', '_title']:
            # _title 轨道可能因未配置而不存在
            if f'llm_vote_score{track}' not in df.columns:
                continue
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

    # --- 3c. 媒体权威性加权列预计算 (Holzman et al. 2023, TAR) ---
    if PANEL_CFG.get('compute_media_authority_weighting', False):
        df = compute_media_authority_weights(df)
        mw = df['media_authority_weight'].fillna(1.0)
        for track in ['_full', '_ctx', '_title']:
            # _title 轨道可能因未配置而不存在
            if f'llm_vote_score{track}' not in df.columns:
                continue
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

    # --- 3d. 跟风衰减加权列预计算 (Tetlock 2011, JF) ---
    if 'herd_weight' in df.columns:
        logger.info("=" * 60)
        logger.info("步骤 3d: 跟风衰减加权列预计算 (HW, 双轨)")
        logger.info("=" * 60)
        hw = df['herd_weight'].fillna(1.0)
        for track in ['_full', '_ctx', '_title']:
            if f'llm_vote_score{track}' not in df.columns:
                continue
            # 情感离散/连续 (遵循 MW 命名模式: _hw 在 track 之前)
            df[f'llm_vote_score_hw{track}'] = df[f'llm_vote_score{track}'] * hw
            df[f'llm_vote_cont_hw{track}'] = df[f'llm_vote_cont{track}'] * hw
            # LLM 逐模型
            for short in LLM_MODELS:
                for sfx in ['_score', '_cont']:
                    src = f'{short}{sfx}{track}'
                    if src in df.columns:
                        df[f'{short}{sfx}_hw{track}'] = df[src] * hw
            # 词典
            for d in DICT_NAMES:
                src = f'{d}_score{track}'
                if src in df.columns:
                    df[f'{d}_score_hw{track}'] = df[src] * hw
                src_idf = f'{d}_idf_score{track}'
                if src_idf in df.columns:
                    df[f'{d}_idf_score_hw{track}'] = df[src_idf] * hw
            # BERT
            for b in BERT_MODELS:
                for label in ['_正面', '_负面']:
                    src = f'{b}{label}{track}'
                    if src in df.columns:
                        df[f'{b}{label}_hw{track}'] = df[src] * hw
        hw_cols = [c for c in df.columns if '_hw' in c]
        logger.info(f"  已生成 {len(hw_cols)} 个跟风衰减加权列")

    # --- 4. 时间解析 ---
    df = parse_time(df)

    # =========================================================================
    # 洗稿率前置列: 多方法 × 双轨篇章级标记
    # =========================================================================
    # 学术依据:
    #   Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
    #   Cheap talk and cherry-picking: What ClimateBert has to say on corporate
    #   climate risk disclosures. Finance Research Letters, 47(Part B), 102776.
    #   https://doi.org/10.1016/j.frl.2022.102776
    #
    # 构造 44 种洗稿率变体 (11 方法 × 双轨 Full/Ctx) 的篇章级标记列:
    #   A:  LLM 多数投票 (is_positive{track}, 双轨)
    #   A2: 单个 LLM (逐 LLM 情感{track} > 0)
    #   B:  反向验证 (负面{track} ∧ 实质性)
    #   D/D2: 词典均值 / 单词典 ({dict}_score{track} > 0)
    #   E/E2: BERT 均值 / 单 BERT ({bert}_正面{track} > 0.5)
    #   F:  高置信度子样本 (agreement_rate{track} ≥ 2/3)
    #   H:  前瞻性空洞法 (正面{track} ∧ 描述性 ∧ fl_ratio{track} > 中位数)
    # 方法 C 和 G 无需篇章级标记, 直接使用面板级已有变量计算
    _tt = df['text_type'].astype(str).str.strip() if 'text_type' in df.columns else None
    _is_desc = (_tt == '描述性') if _tt is not None else None
    _is_sub  = (_tt == '实质性') if _tt is not None else None

    for track in ['_full', '_ctx']:
        pos_col = f'is_positive{track}'
        neg_col = f'is_negative{track}'
        if pos_col not in df.columns or _is_desc is None:
            continue

        # --- 方法 A: LLM 投票 (正面 ∧ 描述性) ---
        df[f'_is_pos_desc{track}'] = (
            (df[pos_col] == 1) & _is_desc
        ).astype(int)

        # --- 方法 B: 反向验证 (负面 ∧ 实质性) ---
        # 学术依据: Deephouse, D.L. (2000). Media reputation as a strategic
        #   resource. Journal of Management, 26(6), 1091-1112.
        #   https://doi.org/10.1177/014920630002600602
        if neg_col in df.columns and _is_sub is not None:
            df[f'_is_neg_sub{track}'] = (
                (df[neg_col] == 1) & _is_sub
            ).astype(int)

        # --- 方法 A2: 单个 LLM (Loughran & McDonald 2016, JAR) ---
        for llm in LLM_MODELS:
            src_col = f'{llm}_score{track}'
            if src_col in df.columns:
                _llm_pos = (df[src_col] > 0)
                df[f'_is_{llm}_positive{track}'] = _llm_pos.astype(int)
                df[f'_is_{llm}_pos_desc{track}'] = (_llm_pos & _is_desc).astype(int)

        # --- 方法 D: 词典均值 (Loughran & McDonald 2011, JF) ---
        _dict_cols = [f'{d}_score{track}' for d in DICT_NAMES
                      if f'{d}_score{track}' in df.columns]
        if _dict_cols:
            df[f'_dict_avg_score{track}'] = df[_dict_cols].mean(axis=1)
            df[f'_is_dict_positive{track}'] = (df[f'_dict_avg_score{track}'] > 0).astype(int)
            df[f'_is_dict_pos_desc{track}'] = (
                (df[f'_is_dict_positive{track}'] == 1) & _is_desc
            ).astype(int)

        # --- 方法 D2: 单个词典 (Gentzkow et al. 2019, JEL) ---
        for d in DICT_NAMES:
            src_col = f'{d}_score{track}'
            if src_col in df.columns:
                _d_pos = (df[src_col] > 0)
                df[f'_is_{d}_positive{track}'] = _d_pos.astype(int)
                df[f'_is_{d}_pos_desc{track}'] = (_d_pos & _is_desc).astype(int)

        # --- 方法 E: BERT 均值 (Huang et al. 2023, CAR) ---
        _bert_pos_cols = [f'{b}_正面{track}' for b in BERT_MODELS
                          if f'{b}_正面{track}' in df.columns]
        if _bert_pos_cols:
            df[f'_bert_avg_pos{track}'] = df[_bert_pos_cols].mean(axis=1)
            df[f'_is_bert_positive{track}'] = (df[f'_bert_avg_pos{track}'] > 0.5).astype(int)
            df[f'_is_bert_pos_desc{track}'] = (
                (df[f'_is_bert_positive{track}'] == 1) & _is_desc
            ).astype(int)

        # --- 方法 E2: 单个 BERT ---
        for b in BERT_MODELS:
            src_col = f'{b}_正面{track}'
            if src_col in df.columns:
                _b_pos = (df[src_col] > 0.5)
                df[f'_is_{b}_positive{track}'] = _b_pos.astype(int)
                df[f'_is_{b}_pos_desc{track}'] = (_b_pos & _is_desc).astype(int)

        # --- 方法 F: 高置信度子样本 (Shapiro et al. 2022, JoE) ---
        agr_col = f'llm_agreement_rate{track}'
        if agr_col in df.columns:
            _hc = df[agr_col].fillna(0) >= 0.67
            df[f'_is_pos_hc{track}'] = ((df[pos_col] == 1) & _hc).astype(int)
            df[f'_is_pos_desc_hc{track}'] = (
                (df[pos_col] == 1) & _is_desc & _hc
            ).astype(int)

        # --- 方法 H: 前瞻性空洞法 (Li 2010, JAR; Bingler et al. 2024, JBF) ---
        fl_col = f'forward_looking_ratio{track}'
        if fl_col in df.columns:
            _fl_median = df[fl_col].median()
            _high_fl = df[fl_col] > _fl_median
            df[f'_is_pos_desc_fl{track}'] = (
                (df[pos_col] == 1) & _is_desc & _high_fl
            ).astype(int)

    _wr_flag_cols = [c for c in df.columns if c.startswith('_is_')]
    logger.info(f"  洗稿率前置列生成完毕: {len(_wr_flag_cols)} 列 (双轨)")

    # --- 5. Bank-Year 聚合 (df 为只读: groupby/filter/merge) ---
    panel = aggregate_panel(df)

    # 引用转移: aggregate_panel 已完成, 后续全部使用 df_exploded
    df_exploded = df
    del df  # 防止后续误用, 对象由 df_exploded 持有不会被回收

    # --- 6. 面板平衡 ---
    panel = balance_panel(panel)

    # --- 6a. has_coverage 哑变量 ---
    panel['has_coverage'] = (panel['n_articles'] > 0).astype(int)
    logger.info(f"  has_coverage: 有报道={panel['has_coverage'].sum()}, "
                f"无报道={len(panel) - panel['has_coverage'].sum()}")

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

    # --- 7c. 银行注册地地理信息 ---
    # 从 bank_addresses.json 合并省份和城市, 用于:
    #   (1) 省级/城市级聚类标准误 (Luo & Li 2025, Table A.2)
    #   (2) 步骤 7d leave-one-out IV 的前置依赖
    panel = merge_bank_geography(panel)

    # --- 7d. Leave-one-out 地理平均情感 (IV) ---
    # 构建同省/同城市其他银行的平均情感 → 工具变量
    # (Luo & Li 2025, Table 3: Province_news_sentiment)
    panel = compute_leave_one_out_sentiment(panel)

    # --- 7d-geo. 四梯度地理距离缓冲 (Gurun & Butler 2012; Engelberg & Parsons 2011) ---
    try:
        if hasattr(_m43, 'compute_geo_proximity_buffers'):
            panel = _m43.compute_geo_proximity_buffers(df_exploded, panel)
        else:
            logger.info("  compute_geo_proximity_buffers 不可用, 跳过")
    except Exception as e:
        logger.warning(f"  四梯度距离缓冲失败: {e}")

    # --- 7d-imit. 区域 AI 模仿渗透率 (六层 LOO, Leary & Roberts 2014) ---
    try:
        if hasattr(_m43, 'compute_regional_imitation_pressure'):
            panel = _m43.compute_regional_imitation_pressure(panel)
        else:
            logger.info("  compute_regional_imitation_pressure 不可用, 跳过")
    except Exception as e:
        logger.warning(f"  区域模仿渗透率失败: {e}")

    # --- 7e. Bartik IV (29套分类维度) ---
    if PANEL_CFG.get('compute_bartik_iv', True):
        logger.info("=" * 60)
        logger.info("步骤 7e: Bartik Shift-Share IV (29套)")
        logger.info("=" * 60)
        type_map, scale_map = load_bank_group_maps()
        T0 = panel['year'].min()

        # --- 主 Bartik: 银行类型 (6类, 5有效IV) ---
        panel = compute_bartik_iv(panel, df_exploded, type_map, 'type')
        # 基期敏感性 (T0, T0+1, T0&T0+1)
        # ⚠️ 使用 merge-based 赋值，避免 .values 行序错配
        for suffix, base_yr in [('_t0', T0), ('_t1', T0+1)]:
            ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                     df_exploded, type_map, 'type',
                                     base_year=base_yr)
            for track in ['_full', '_ctx', '_title']:
                src_col = f'bartik_type_iv{track}'
                dst_col = f'bartik_type_iv{track}{suffix}'
                ptmp = ptmp.rename(columns={src_col: dst_col})
            panel = panel.merge(
                ptmp[['target_bank', 'year',
                      f'bartik_type_iv_full{suffix}',
                      f'bartik_type_iv_ctx{suffix}']],
                on=['target_bank', 'year'], how='left')
        base_t01 = df_exploded[df_exploded['year'].isin([T0, T0+1])]
        ptmp = compute_bartik_iv(panel[['target_bank', 'year']].copy(),
                                 base_t01, type_map, 'type', base_year=T0)
        for track in ['_full', '_ctx', '_title']:
            src_col = f'bartik_type_iv{track}'
            ptmp = ptmp.rename(columns={src_col: f'bartik_type_iv{track}_t01'})
        panel = panel.merge(
            ptmp[['target_bank', 'year',
                  'bartik_type_iv_full_t01',
                  'bartik_type_iv_ctx_t01']],
            on=['target_bank', 'year'], how='left')

        # --- 稳健性 1: 银行规模 (4类, 3有效IV) ---
        panel = compute_bartik_iv(panel, df_exploded, scale_map, 'scale')

        # --- 7e-digfront. 数字化前沿距离代理变量 ---
        # 按同类型银行的年度中位数新闻覆盖量划分 (仅有新闻覆盖的银行参与)
        # 概念迁移自:
        #   Goldfarb, A. & Tucker, C. (2019). Digital economics.
        #   Journal of Economic Literature, 57(1), 3-43.
        #   https://doi.org/10.1257/jel.20171452
        # 用途: DDD 三重差分 — 数字化前沿 × 政策冲击 (步骤 7g 后构建)
        if 'bank_type' in panel.columns:
            _has_news_df = panel['n_articles'] > 0
            _grp_median = panel[_has_news_df].groupby(
                ['bank_type', 'year'])['n_articles'].transform('median')
            panel['digital_frontier'] = 0
            panel.loc[_has_news_df, 'digital_frontier'] = (
                panel.loc[_has_news_df, 'n_articles'] >= _grp_median
            ).astype(int)
            logger.info(f"  digital_frontier: "
                        f"1={panel['digital_frontier'].sum()}, "
                        f"0={(panel['digital_frontier'] == 0).sum()}")
        else:
            logger.warning("  bank_type 不存在, 跳过 digital_frontier 构建")

        # --- 稳健性 2: 金融科技类型 (2类, 1有效IV) ---
        fintech_map = {'底层技术': 'tech', '应用场景': 'app'}
        panel = compute_bartik_iv_fintech(panel, df_exploded, fintech_map, 'fintech')

        # --- 稳健性 3-6: 媒体分类 Bartik (4种分类方式) ---
        # 3=财经/综合 4=中央/地方 5=财经/非财经 6=综合/非综合
        cls_path = os.path.join(os.path.dirname(__file__),
                                'config', 'media_classification.json')
        if os.path.exists(cls_path):
            with open(cls_path, 'r', encoding='utf-8') as f:
                media_cls = json.load(f)
            FIN = set(media_cls.get('financial_media', []))
            COMP = set(media_cls.get('comprehensive_media', []))
            CENTRAL = set(media_cls.get('central_media', []))
            media_col = '媒体(中文)'

            # 3a: 财经/综合/其他
            if '_media_type' not in df_exploded.columns:
                df_exploded['_media_type'] = df_exploded[media_col].apply(
                    lambda x: 'fin' if x in FIN else ('comp' if x in COMP else 'other')
                )
            media_map = {'fin': 'fin', 'comp': 'comp', 'other': 'other'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, media_map, 'media',
                category_col='_media_type'
            )

            # 3b: 中央级/地方级
            df_exploded['_media_central'] = df_exploded[media_col].apply(
                lambda x: 'central' if x in CENTRAL else 'local'
            )
            mcentral_map = {'central': 'central', 'local': 'local'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcentral_map, 'mcentral',
                category_col='_media_central'
            )

            # 3c: 财经/非财经
            df_exploded['_media_fin_binary'] = df_exploded[media_col].apply(
                lambda x: 'fin' if x in FIN else 'nonfin'
            )
            mfin_map = {'fin': 'fin', 'nonfin': 'nonfin'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mfin_map, 'mfin',
                category_col='_media_fin_binary'
            )

            # 3d: 综合性/非综合性
            df_exploded['_media_comp_binary'] = df_exploded[media_col].apply(
                lambda x: 'comp' if x in COMP else 'noncomp'
            )
            mcomp_map = {'comp': 'comp', 'noncomp': 'noncomp'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcomp_map, 'mcomp',
                category_col='_media_comp_binary'
            )

            logger.info(f"  媒体分类 Bartik: 3a(fin/comp/other) + "
                        f"3b(central/local) + 3c(fin/nonfin) + 3d(comp/noncomp)")

            # --- 新增四维度媒体分类 Bartik (3e-3i) ---
            OFFICIAL = set(media_cls.get('official_media', []))
            MARKET = set(media_cls.get('market_media', []))
            DEEPDIVE = set(media_cls.get('deep_dive_periodicals', []))
            DAILY = set(media_cls.get('high_frequency_dailies', []))

            # 3e: 官方/非官方
            df_exploded['_media_official_binary'] = df_exploded[media_col].apply(
                lambda x: 'official' if x in OFFICIAL else 'nonoff'
            )
            mofficial_map = {'official': 'official', 'nonoff': 'nonoff'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mofficial_map, 'mofficial',
                category_col='_media_official_binary'
            )

            # 3f: 市场化/非市场化
            df_exploded['_media_market_binary'] = df_exploded[media_col].apply(
                lambda x: 'market' if x in MARKET else 'nonmkt'
            )
            mmarket_map = {'market': 'market', 'nonmkt': 'nonmkt'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mmarket_map, 'mmarket',
                category_col='_media_market_binary'
            )

            # 3g: 深度/日报/其他 (三方)
            df_exploded['_media_freq_type'] = df_exploded[media_col].apply(
                lambda x: 'deepdive' if x in DEEPDIVE else ('daily' if x in DAILY else 'other')
            )
            mfreq_map = {'deepdive': 'deepdive', 'daily': 'daily', 'other': 'other'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mfreq_map, 'mfreq',
                category_col='_media_freq_type'
            )

            # 3h: 深度/非深度
            df_exploded['_media_deep_binary'] = df_exploded[media_col].apply(
                lambda x: 'deepdive' if x in DEEPDIVE else 'nondeep'
            )
            mdeep_map = {'deepdive': 'deepdive', 'nondeep': 'nondeep'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mdeep_map, 'mdeep',
                category_col='_media_deep_binary'
            )

            # 3i: 日报/非日报
            df_exploded['_media_daily_binary'] = df_exploded[media_col].apply(
                lambda x: 'daily' if x in DAILY else 'nondaily'
            )
            mdaily_map = {'daily': 'daily', 'nondaily': 'nondaily'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mdaily_map, 'mdaily',
                category_col='_media_daily_binary'
            )

            logger.info(f"  新增媒体 Bartik: 3e(official/nonoff) + "
                        f"3f(market/nonmkt) + 3g(freq-3way) + "
                        f"3h(deep/nondeep) + 3i(daily/nondaily)")
        else:
            logger.warning("  media_classification.json 不存在, 跳过所有媒体分类 Bartik")

        # --- 稳健性 7: 媒体省份 ---
        MPROV_MIN_ARTICLES = 5
        mprov_col = '国家地区/省份'
        if mprov_col in df_exploded.columns:
            prov_counts = df_exploded[mprov_col].value_counts()
            valid_provs = set(prov_counts[prov_counts >= MPROV_MIN_ARTICLES].index)
            mprov_map = {p: p for p in valid_provs}
            mprov_map['other'] = 'other'
            df_exploded['_media_province'] = df_exploded[mprov_col].apply(
                lambda x: x if x in valid_provs else 'other'
            )
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mprov_map, 'mprov',
                category_col='_media_province'
            )
            logger.info(f"  媒体省份 Bartik: {len(valid_provs)} 个有效省份")
        else:
            logger.warning(f"  列 '{mprov_col}' 不存在, 跳过媒体省份 Bartik")

        # --- 稳健性 8: 媒体权威性 ---
        mw_path = os.path.join(os.path.dirname(__file__),
                               'config', 'media_weights.json')
        if os.path.exists(mw_path):
            with open(mw_path, 'r', encoding='utf-8') as f:
                mw = json.load(f)
            mw = {k: v for k, v in mw.items() if not k.startswith('//')}
            media_col = '媒体(中文)'
            df_exploded['_media_authority'] = df_exploded[media_col].apply(
                lambda x: 'high' if mw.get(x, 10) >= 80
                          else ('mid' if mw.get(x, 10) >= 60 else 'low')
            )
            mauth_map = {'high': 'high', 'mid': 'mid', 'low': 'low'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mauth_map, 'mauth',
                category_col='_media_authority'
            )
        else:
            logger.warning("  media_weights.json 不存在, 跳过媒体权威性 Bartik")

        # --- 稳健性 9: 文章长度 ---
        if 'doc_length' in df_exploded.columns:
            year_median_doclen = df_exploded.groupby('year')['doc_length'].transform('median')
            df_exploded['_doclen_type'] = np.where(
                df_exploded['doc_length'] > year_median_doclen,
                'long', 'short'
            )
            doclen_map = {'long': 'long', 'short': 'short'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, doclen_map, 'doclen',
                category_col='_doclen_type'
            )
        else:
            logger.warning("  doc_length 列不存在, 跳过文章长度 Bartik")

        # --- 稳健性 10-13: 时间维度 (半年度/季度/月度/工作日) ---
        date_col = '日期'
        if date_col in df_exploded.columns:
            # 向量化日期特征提取 (parse_time L780 已确保 datetime 类型)
            _month = df_exploded[date_col].dt.month
            _dow   = df_exploded[date_col].dt.dayofweek
            df_exploded['_half_year']  = np.where(_month <= 6, 'H1', 'H2')
            df_exploded['_quarter']    = 'Q' + ((_month - 1) // 3 + 1).astype(str)
            df_exploded['_pub_month']  = 'M' + _month.astype(str).str.zfill(2)
            df_exploded['_wkday_type'] = np.where(_dow >= 5, 'weekend', 'weekday')

            # 稳健性 10: 半年度
            half_map = {'H1': 'H1', 'H2': 'H2'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, half_map, 'half',
                category_col='_half_year'
            )
            # 稳健性 11: 季度
            qtr_map = {'Q1': 'Q1', 'Q2': 'Q2', 'Q3': 'Q3', 'Q4': 'Q4'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, qtr_map, 'qtr',
                category_col='_quarter'
            )
            # 稳健性 12: 月度
            month_map = {f'M{m:02d}': f'M{m:02d}' for m in range(1, 13)}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, month_map, 'month',
                category_col='_pub_month'
            )
            # 稳健性 13: 工作日/周末
            wkday_map = {'weekday': 'weekday', 'weekend': 'weekend'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, wkday_map, 'wkday',
                category_col='_wkday_type'
            )
        else:
            logger.warning(f"  列 '{date_col}' 不存在, 跳过时间维度 Bartik (稳健性 10-13)")

        # --- 稳健性 14: 专属/共享报道 ---
        if 'is_multi_bank' in df_exploded.columns:
            df_exploded['_excl_type'] = df_exploded['is_multi_bank'].map(
                {0: 'exclusive', 1: 'shared'}
            )
            excl_map = {'exclusive': 'exclusive', 'shared': 'shared'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, excl_map, 'excl',
                category_col='_excl_type'
            )
        else:
            logger.warning("  is_multi_bank 列不存在, 跳过专属/共享 Bartik")

        # --- 稳健性 15: 地理邻近性 ---
        media_prov_col = '国家地区/省份'
        if media_prov_col in df_exploded.columns:
            addr_path = os.path.join(os.path.dirname(__file__),
                                     'config', 'bank_addresses.json')
            if os.path.exists(addr_path):
                with open(addr_path, 'r', encoding='utf-8') as f:
                    _addr = json.load(f)
                _prov_map = {k: v.get('province', '') for k, v in _addr.items()}
                df_exploded['_bank_prov'] = df_exploded['target_bank'].map(_prov_map)
                df_exploded['_geo_proximity'] = np.where(
                    df_exploded[media_prov_col] == df_exploded['_bank_prov'],
                    'local', 'nonlocal'
                )
                geoprox_map = {'local': 'local', 'nonlocal': 'nonlocal'}
                panel = compute_bartik_iv_fintech(
                    panel, df_exploded, geoprox_map, 'geoprox',
                    category_col='_geo_proximity'
                )

        # --- 稳健性 16: 标题出现 ---
        if 'target_bank_in_title' in df_exploded.columns:
            df_exploded['_title_type'] = df_exploded['target_bank_in_title'].map(
                {1: 'title', 0: 'body'}
            )
            title_map = {'title': 'title', 'body': 'body'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, title_map, 'title',
                category_col='_title_type'
            )

        # --- 稳健性 17: 关键词多样性 ---
        if 'fintech_distinct_keywords' in df_exploded.columns:
            year_median_kwdiv = df_exploded.groupby('year')['fintech_distinct_keywords'].transform('median')
            df_exploded['_kwdiv_type'] = np.where(
                df_exploded['fintech_distinct_keywords'] > year_median_kwdiv,
                'high_div', 'low_div'
            )
            kwdiv_map = {'high_div': 'high_div', 'low_div': 'low_div'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, kwdiv_map, 'kwdiv',
                category_col='_kwdiv_type'
            )

        # --- 稳健性 18: 关键词密度 ---
        if 'fintech_total_count' in df_exploded.columns:
            year_median_kwden = df_exploded.groupby('year')['fintech_total_count'].transform('median')
            df_exploded['_kwden_type'] = np.where(
                df_exploded['fintech_total_count'] > year_median_kwden,
                'dense', 'sparse'
            )
            kwden_map = {'dense': 'dense', 'sparse': 'sparse'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, kwden_map, 'kwden',
                category_col='_kwden_type'
            )

        # --- 稳健性 19: 提及密度 ---
        if 'mention_density' in df_exploded.columns:
            year_median_mden = df_exploded.groupby('year')['mention_density'].transform('median')
            df_exploded['_mden_type'] = np.where(
                df_exploded['mention_density'] > year_median_mden,
                'deep', 'shallow'
            )
            mden_map = {'deep': 'deep', 'shallow': 'shallow'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mden_map, 'mden',
                category_col='_mden_type'
            )

        # --- 稳健性 20: 银行提及次数 ---
        if 'target_bank_mention_count' in df_exploded.columns:
            df_exploded['_mcount_type'] = pd.cut(
                df_exploded['target_bank_mention_count'],
                bins=[-1, 3, 4, float('inf')],  # -1 确保 mention_count=0 也被覆盖
                labels=['low', 'mid', 'high']
            ).astype(str)  # Categorical → str, 避免下游 map() 兼容性问题
            mcount_map = {'low': 'low', 'mid': 'mid', 'high': 'high'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, mcount_map, 'mcount',
                category_col='_mcount_type'
            )

        # --- 稳健性 21: 媒体覆盖广度 ---
        media_col = '媒体(中文)'
        if media_col in df_exploded.columns:
            media_bank_counts = df_exploded.groupby(media_col)['target_bank'].nunique()
            median_cov = media_bank_counts.median()
            broad_set = set(media_bank_counts[media_bank_counts > median_cov].index)
            df_exploded['_breadth_type'] = df_exploded[media_col].apply(
                lambda m: 'broad' if m in broad_set else 'niche'
            )
            breadth_map = {'broad': 'broad', 'niche': 'niche'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, breadth_map, 'breadth',
                category_col='_breadth_type'
            )

        # --- 稳健性 22: 前瞻性语言 ---
        if 'forward_looking_ratio_full' in df_exploded.columns:
            year_median_fl = df_exploded.groupby('year')['forward_looking_ratio_full'].transform('median')
            df_exploded['_fwdlook_type'] = np.where(
                df_exploded['forward_looking_ratio_full'] > year_median_fl,
                'forward', 'backward'
            )
            fwdlook_map = {'forward': 'forward', 'backward': 'backward'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, fwdlook_map, 'fwdlook',
                category_col='_fwdlook_type'
            )

        # --- 稳健性 23: 平均句长 ---
        if 'avg_sentence_len_full' in df_exploded.columns:
            year_median_sl = df_exploded.groupby('year')['avg_sentence_len_full'].transform('median')
            df_exploded['_sentlen_type'] = np.where(
                df_exploded['avg_sentence_len_full'] > year_median_sl,
                'complex', 'simple'
            )
            sentlen_map = {'complex': 'complex', 'simple': 'simple'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, sentlen_map, 'sentlen',
                category_col='_sentlen_type'
            )

        # --- 稳健性 24: 词汇丰富度 TTR ---
        if 'type_token_ratio_full' in df_exploded.columns:
            year_median_ttr = df_exploded.groupby('year')['type_token_ratio_full'].transform('median')
            df_exploded['_ttr_type'] = np.where(
                df_exploded['type_token_ratio_full'] > year_median_ttr,
                'diverse', 'uniform'
            )
            ttr_map = {'diverse': 'diverse', 'uniform': 'uniform'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, ttr_map, 'ttr',
                category_col='_ttr_type'
            )

        # --- 稳健性 25: 出版形态 ---
        if '媒体类型(中文)' in df_exploded.columns:
            pubfmt_map_raw = {
                '报纸': 'newspaper', '杂志': 'magazine', '新闻通讯社': 'agency'
            }
            df_exploded['_pubformat'] = df_exploded['媒体类型(中文)'].map(pubfmt_map_raw).fillna('newspaper')
            pubfmt_map = {'newspaper': 'newspaper', 'magazine': 'magazine', 'agency': 'agency'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, pubfmt_map, 'pubfmt',
                category_col='_pubformat'
            )

        # --- 稳健性 26: 作者署名 ---
        if '作者' in df_exploded.columns:
            df_exploded['_author_type'] = np.where(
                df_exploded['作者'].notna() & (df_exploded['作者'].astype(str).str.strip() != ''),
                'named', 'anonymous'
            )
            author_map = {'named': 'named', 'anonymous': 'anonymous'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, author_map, 'author',
                category_col='_author_type'
            )

        # --- 稳健性 27: 版面位置 ---
        if '版面' in df_exploded.columns:
            front_page_keywords = ['头版', '要闻', '头条']
            df_exploded['_section_pos'] = np.where(
                df_exploded['版面'].fillna('').str.contains('|'.join(front_page_keywords)),
                'front_page', 'inner'
            )
            page_map = {'front_page': 'front_page', 'inner': 'inner'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, page_map, 'page',
                category_col='_section_pos'
            )

        # --- 稳健性 28: 页号位置 ---
        if '页号' in df_exploded.columns:
            def extract_page_num(x):
                if pd.isna(x):
                    return np.nan
                nums = re.findall(r'\d+', str(x))
                return int(nums[0]) if nums else np.nan
            df_exploded['_page_numeric'] = df_exploded['页号'].apply(extract_page_num)
            df_exploded['_pgnum_type'] = np.where(
                df_exploded['_page_numeric'].fillna(99) <= 3,
                'early_page', 'late_page'
            )
            pgnum_map = {'early_page': 'early_page', 'late_page': 'late_page'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, pgnum_map, 'pgnum',
                category_col='_pgnum_type'
            )

        logger.info(f"  Bartik IV 共29套已完成")

    # --- 7f. 经济圈 Leave-One-Out IV ---
    if PANEL_CFG.get('compute_bartik_iv', True):
        logger.info("=" * 60)
        logger.info("步骤 7f: 经济圈 Leave-One-Out IV")
        logger.info("=" * 60)
        panel = compute_zone_leave1out(panel, df_exploded)

    # --- 7g. DID 政策冲击变量 ---
    if PANEL_CFG.get('compute_policy_shocks', True):
        logger.info("=" * 60)
        logger.info("步骤 7g: DID 政策冲击变量 (DCEP + Sandbox)")
        logger.info("=" * 60)
        panel = merge_policy_shocks(panel)

    # =========================================================================
    # 步骤 7g-het: 异质性分析交互项预计算
    # =========================================================================
    # 总体学术依据:
    #   Angrist, J.D. & Pischke, J.-S. (2009). Mostly Harmless Econometrics:
    #   An Empiricist's Companion. Princeton University Press.
    #   https://doi.org/10.1515/9781400829828
    #   → §3.4.2: 交互项优于中介回归，避免"Bad Controls"问题
    #
    #   Brambor, T., Clark, W.R. & Golder, M. (2006). Understanding interaction
    #   models: Improving empirical analyses. Political Analysis, 14(1), 63-82.
    #   https://doi.org/10.1093/pan/mpi014
    #   → 交互项模型中主效应 (constituent terms) 必须同时进入回归，否则系数有偏
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7g-het: 异质性分析交互项预计算")
    logger.info("=" * 60)

    # --- (a) SOE 哑变量 ---
    # bank_type 由步骤 7e compute_bartik_iv() 生成
    if 'bank_type' in panel.columns:
        panel['is_soe'] = (panel['bank_type'] == 'soe').astype(int)
        logger.info(f"  is_soe: SOE={panel['is_soe'].sum()}, "
                    f"非SOE={(panel['is_soe'] == 0).sum()}")
    else:
        logger.warning("  bank_type 不存在, is_soe 设为 0")
        panel['is_soe'] = 0

    # --- (b) bank_scale 有序编码 ---
    # scale_map: 'L'/'M'/'S'/'XS'/'other' (44_panel_iv_did.py L58-59)
    scale_map_ord = {'XS': 1, 'S': 2, 'M': 3, 'L': 4}
    if 'bank_scale' in panel.columns:
        panel['bank_scale_ord'] = panel['bank_scale'].map(
            scale_map_ord).fillna(0).astype(int)
        logger.info(f"  bank_scale_ord 分布: "
                    f"{panel['bank_scale_ord'].value_counts().sort_index().to_dict()}")
    else:
        logger.warning("  bank_scale 不存在, bank_scale_ord 设为 0")
        panel['bank_scale_ord'] = 0

    # --- (c) 覆盖强度分组 (替代二元 has_coverage) ---
    # 仅在有新闻覆盖的银行中按年度中位数分组
    # 学术依据:
    #   Fang, L.H. & Peress, J. (2009). Media coverage and the cross-section
    #   of stock returns. Journal of Finance, 64(5), 2023-2052.
    #   https://doi.org/10.1111/j.1540-6261.2009.01493.x
    #   → 媒体覆盖的边际效应递减，需区分高低覆盖强度
    # ⚠️ 注意: 原始 has_coverage (0/1) 与 tone 的交互项无额外信息 (冗余):
    #   零新闻行 tone=NaN → tone×has_coverage=NaN (非0);
    #   有新闻行 tone×1=tone → 交互项退化为 tone 本身，无增量信息
    has_news_het = panel['n_articles'] > 0
    year_median_cov = panel[has_news_het].groupby(
        'year')['n_articles'].transform('median')
    panel['high_coverage'] = 0
    panel.loc[has_news_het, 'high_coverage'] = (
        panel.loc[has_news_het, 'n_articles'] >= year_median_cov
    ).astype(int)
    logger.info(f"  high_coverage: 1={panel['high_coverage'].sum()}, "
                f"0={(panel['high_coverage'] == 0).sum()}")

    # --- (d) 交互项构建 (双轨: _full + _ctx) ---
    het_count = 0
    for track in ['_full', '_ctx']:
        tone = f'llm_vote_tone{track}'
        if tone not in panel.columns:
            continue
        panel[f'tone_x_soe{track}'] = panel[tone] * panel['is_soe']
        panel[f'tone_x_scale{track}'] = panel[tone] * panel['bank_scale_ord']
        panel[f'tone_x_highcov{track}'] = panel[tone] * panel['high_coverage']
        het_count += 3
    logger.info(f"  已生成 {het_count} 个异质性交互项 (Tone × SOE/Scale/HighCov)")

    # --- (e) DDD 三重差分交互项 ---
    # 学术依据:
    #   Wooldridge, J.M. (2010). Econometric Analysis of Cross Section and
    #   Panel Data (2nd ed.). MIT Press. ISBN: 978-0-262-23258-6
    #   → §10.4: 三重差分要求 Stata 中同时纳入所有低阶交互项 (## 语法自动满足)
    ddd_count = 0
    for prefix in ['dcep', 'sandbox']:
        t_col, p_col = f'{prefix}_treated', f'{prefix}_post'
        if (t_col in panel.columns and p_col in panel.columns
                and 'digital_frontier' in panel.columns):
            panel[f'{prefix}_ddd_digfront'] = (
                panel[t_col] * panel[p_col] * panel['digital_frontier']
            )
            ddd_count += 1
    if ddd_count > 0:
        logger.info(f"  已生成 {ddd_count} 个 DDD 三重差分交互项 "
                    f"(Treated × Post × DigFrontier)")
    else:
        logger.info("  DDD 交互项跳过 (DID 变量或 digital_frontier 不存在)")

    # --- (f) 银行业压力期非对称效应 ---
    # 学术依据:
    #   García, D. (2013). Sentiment during recessions. Journal of Finance,
    #   68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
    #   → 衰退/压力期间情感指标的统计特征显著不同于常规期
    # 压力年份定义与 51_falsification_test.py L897-899 一致
    STRESS_YEARS = {2015, 2018, 2020}  # 股灾、去杠杆、疫情
    panel['stress_period'] = panel['year'].isin(STRESS_YEARS).astype(int)
    stress_count = 0
    for track in ['_full', '_ctx']:
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'tone_x_stress{track}'] = panel[tone] * panel['stress_period']
            stress_count += 1
    logger.info(f"  stress_period: 压力年={panel['stress_period'].sum()}, "
                f"常规年={(panel['stress_period'] == 0).sum()} "
                f"({stress_count} 个交互项)")

    # --- (g) 存款保险制度时间断点调节项 ---
    # 《存款保险条例》(国务院令第660号) 2015.05.01 全国统一施行
    # 设计: 时间断点调节项, 非 DID (全国统一实施, 无处理/控制分组)
    # ⚠️ 不可通过 policy_shocks.json 实现:
    #   merge_policy_shocks() 通过 panel['bank_province'].isin(provs) 匹配,
    #   "全国" 不是有效省份名 (44_panel_iv_did.py L513-517)
    panel['depins_post'] = (panel['year'] >= 2015).astype(int)
    depins_count = 0
    for track in ['_full', '_ctx']:
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'tone_x_depins{track}'] = panel[tone] * panel['depins_post']
            depins_count += 1
    logger.info(f"  depins_post: 实施后={panel['depins_post'].sum()}, "
                f"实施前={(panel['depins_post'] == 0).sum()} "
                f"({depins_count} 个交互项)")

    # --- (h) 复合关注度指数 (Concern Score) ---
    # 公式: concern_score = ln_news_coverage × (senti_ratio + 1) / 2
    # 其中 senti_ratio = (neg_count - pos_count) / (neg_count + pos_count) ∈ [-1, 1]
    # → concern_score ∈ [0, ∞): 越高 = 越多负面新闻 + 越多报道量
    # ⚠️ 全中性文章 (pos=neg=0): total_pn=0 → senti_ratio=NaN → concern_score=NaN
    #   (语义合理: 无正/负方向性信息时, 关注度方向未定义)
    concern_count = 0
    for track in ['_full', '_ctx']:
        pos_c, neg_c = f'pos_count{track}', f'neg_count{track}'
        if pos_c in panel.columns and neg_c in panel.columns:
            total_pn = panel[pos_c] + panel[neg_c]
            safe_total = total_pn.replace(0, np.nan)
            senti_ratio = (panel[neg_c] - panel[pos_c]) / safe_total
            panel[f'concern_score{track}'] = (
                panel['ln_news_coverage'] * (senti_ratio + 1) / 2
            )
            concern_count += 1
    logger.info(f"  已生成 {concern_count} 个 concern_score 变量")

    # --- (i) 情感滞后与反转效应 ---
    # 学术依据:
    #   De Bondt, W.F.M. & Thaler, R. (1985). Does the stock market overreact?
    #   Journal of Finance, 40(3), 793-805.
    #   https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
    #   → 过度反应假说: 前期极端情感 → 后期均值回归/反转
    # ⚠️ balance_panel() 确保面板为完全笛卡尔积 (银行×年份),
    #   shift(1) 不会跳过年份。首年滞后值为 NaN (预期行为)
    panel = panel.sort_values(['target_bank', 'year'])
    lag_count = 0
    for track in ['_full', '_ctx']:
        tone = f'llm_vote_tone{track}'
        if tone in panel.columns:
            panel[f'{tone}_lag1'] = panel.groupby('target_bank')[tone].shift(1)
            panel[f'tone_reversal{track}'] = panel[tone] - panel[f'{tone}_lag1']
            lag_count += 2
    logger.info(f"  已生成 {lag_count} 个滞后/反转变量 (lag1 + reversal)")

    logger.info(f"  ── 异质性分析交互项预计算完成 ──")

    # --- 7h-net. 同行网络传染/溢出效应 (Leary & Roberts 2014, JF) ---
    if compute_network_spillovers is not None:
        logger.info("=" * 60)
        logger.info("步骤 7h-net: 同行网络传染/溢出效应")
        logger.info("=" * 60)
        panel = compute_network_spillovers(panel, df_exploded)
    else:
        logger.info("  46_network_spillovers.py 不存在, 跳过网络溢出计算")

    # --- 7h-cent. 银行共现网络中心度 (Freeman 1979; Billio et al. 2012) ---
    if compute_bank_network_centrality is not None:
        panel = compute_bank_network_centrality(panel, df_exploded)
    else:
        logger.info("  compute_bank_network_centrality 不可用, 跳过")

    # --- 7h-cogn. 认知邻近度 (Boschma 2005; Dahlke et al. 2024) ---
    if compute_cognitive_proximity is not None:
        panel = compute_cognitive_proximity(df_exploded, panel)
    else:
        logger.info("  compute_cognitive_proximity 不可用, 跳过")

    # --- 7h-brok. 信息经纪网络中心度 (Han et al. 2024, RFS) ---
    if compute_brokerage_centrality is not None:
        panel = compute_brokerage_centrality(panel, df_exploded)
    else:
        logger.info("  compute_brokerage_centrality 不可用, 跳过")

    # --- 7h-neg. 行业负面冲击指数 (LOO, Manski 1993) ---
    if compute_industry_neg_shock is not None:
        panel = compute_industry_neg_shock(panel)
    else:
        logger.info("  compute_industry_neg_shock 不可用, 跳过")

    # --- 7h-fire. 火灾甩卖交乘项 (依赖 brokerage + neg_shock) ---
    if compute_fire_sale_interaction is not None:
        panel = compute_fire_sale_interaction(panel)
    else:
        logger.info("  compute_fire_sale_interaction 不可用, 跳过")

    # =========================================================================
    # 步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 双轨构造
    # =========================================================================
    # 学术依据:
    #   Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
    #   Cheap talk and cherry-picking. Finance Research Letters, 47(B), 102776.
    #   https://doi.org/10.1016/j.frl.2022.102776
    #
    # 构造 44 种洗稿率变体 (11 方法 × 双轨 Full/Ctx):
    #   A/A2: LLM 投票 + 单 LLM (3模型) × 双轨
    #   B:    反向验证 + 非对称性 × 双轨
    #   C:    情感纯度缺口 × 双轨
    #   D/D2: 词典均值 + 单词典 (5本) × 双轨
    #   E/E2: BERT 均值 + 单 BERT (5模型) × 双轨
    #   F:    高置信度子样本 × 双轨
    #   G:    描述性文章情感偏移 × 双轨
    #   H:    前瞻性空洞 × 双轨
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 双轨构造 (44种)")
    logger.info("=" * 60)

    def _safe_ratio(numer, denom):
        """安全除法: 分母 <= 0 时返回 NaN, 使用 np.divide + where 避免 RuntimeWarning。"""
        out = np.full(len(denom), np.nan)
        mask = np.asarray(denom) > 0
        np.divide(np.asarray(numer), np.asarray(denom), out=out, where=mask)
        return out

    wr_variants = {}  # {变量名: 描述}

    for track in ['_full', '_ctx']:
        _sfx = '' if track == '_full' else '_ctx'  # Full 不加后缀 (主指标)
        pos_col = f'pos_count{track}'

        # --- 方法 A: LLM 投票极化条件法 ---
        pd_col = f'pos_desc_count{track}'
        vn = f'washing_ratio{_sfx}'
        if pos_col in panel.columns and pd_col in panel.columns:
            panel[vn] = _safe_ratio(panel[pd_col], panel[pos_col])
            wr_variants[vn] = f'A: LLM投票{track}'

        # --- 方法 A2: 单个 LLM ---
        for llm in LLM_MODELS:
            pc = f'{llm}_pos_count{track}'
            pdc = f'{llm}_pos_desc_count{track}'
            vn = f'washing_ratio_{llm}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(panel[pdc], panel[pc])
                wr_variants[vn] = f'A2: {llm}{track}'

        # --- 方法 B: 反向验证 ---
        neg_col = f'neg_count{track}'
        ns_col = f'neg_sub_count{track}'
        if neg_col in panel.columns and ns_col in panel.columns:
            vn_r = f'neg_sub_ratio{track}'
            panel[vn_r] = _safe_ratio(panel[ns_col], panel[neg_col])
            wr_variants[vn_r] = f'B: 负面实质性{track}'
            # 非对称性
            wr_a = f'washing_ratio{_sfx}'
            if wr_a in panel.columns:
                vn_asym = f'washing_asymmetry{track}'
                panel[vn_asym] = panel[vn_r] - (1 - panel[wr_a])
                wr_variants[vn_asym] = f'B: 非对称性{track}'

        # --- 方法 C: 情感纯度缺口 ---
        sub_col = f'llm_vote_tone_sub{track}'
        desc_col = f'llm_vote_tone_desc{track}'
        if sub_col in panel.columns and desc_col in panel.columns:
            vn = f'tone_gap_desc_sub{track}'
            panel[vn] = panel[desc_col] - panel[sub_col]
            wr_variants[vn] = f'C: 情感缺口{track}'

        # --- 方法 D: 词典均值 ---
        dpc = f'dict_pos_count{track}'
        dpdc = f'dict_pos_desc_count{track}'
        if dpc in panel.columns and dpdc in panel.columns:
            vn = f'washing_ratio_dict{_sfx}'
            panel[vn] = _safe_ratio(panel[dpdc], panel[dpc])
            wr_variants[vn] = f'D: 词典均值{track}'

        # --- 方法 D2: 单个词典 ---
        for d in DICT_NAMES:
            pc = f'{d}_pos_count{track}'
            pdc = f'{d}_pos_desc_count{track}'
            vn = f'washing_ratio_{d}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(panel[pdc], panel[pc])
                wr_variants[vn] = f'D2: {d}{track}'

        # --- 方法 E: BERT 均值 ---
        bpc = f'bert_pos_count{track}'
        bpdc = f'bert_pos_desc_count{track}'
        if bpc in panel.columns and bpdc in panel.columns:
            vn = f'washing_ratio_bert{_sfx}'
            panel[vn] = _safe_ratio(panel[bpdc], panel[bpc])
            wr_variants[vn] = f'E: BERT均值{track}'

        # --- 方法 E2: 单个 BERT ---
        for b in BERT_MODELS:
            pc = f'{b}_pos_count{track}'
            pdc = f'{b}_pos_desc_count{track}'
            vn = f'washing_ratio_{b}{_sfx}'
            if pc in panel.columns and pdc in panel.columns:
                panel[vn] = _safe_ratio(panel[pdc], panel[pc])
                wr_variants[vn] = f'E2: {b}{track}'

        # --- 方法 F: 高置信度子样本 ---
        hpc = f'pos_hc_count{track}'
        hpdc = f'pos_desc_hc_count{track}'
        if hpc in panel.columns and hpdc in panel.columns:
            vn = f'washing_ratio_hc{_sfx}'
            panel[vn] = _safe_ratio(panel[hpdc], panel[hpc])
            wr_variants[vn] = f'F: 高置信{track}'

        # --- 方法 G: 情感偏移 ---
        desc_tone = f'llm_vote_tone_desc{track}'
        all_tone = f'llm_vote_tone{track}'
        if desc_tone in panel.columns and all_tone in panel.columns:
            vn = f'washing_tone_shift{track}'
            panel[vn] = panel[desc_tone] - panel[all_tone]
            wr_variants[vn] = f'G: 情感偏移{track}'

        # --- 方法 H: 前瞻性空洞 ---
        flc = f'pos_desc_fl_count{track}'
        if flc in panel.columns and pos_col in panel.columns:
            vn = f'washing_ratio_fl{_sfx}'
            panel[vn] = _safe_ratio(panel[flc], panel[pos_col])
            wr_variants[vn] = f'H: 前瞻性{track}'

    # --- Dummy: 全年无正面新闻 ---
    if 'pos_count_full' in panel.columns:
        panel['dummy_no_positive_news'] = (panel['pos_count_full'] <= 0).astype(int)
        logger.info(f"  dummy_no_positive_news=1: {panel['dummy_no_positive_news'].sum():,} 个 Bank-Year")

    # --- 诊断日志 ---
    logger.info(f"  洗稿率变体数: {len(wr_variants)}")
    for var_name, desc in wr_variants.items():
        if var_name in panel.columns:
            valid = panel[var_name].dropna()
            if len(valid) > 0:
                logger.info(f"    {var_name} [{desc}]: "
                            f"n={len(valid):,}, mean={valid.mean():.4f}, "
                            f"std={valid.std():.4f}")
            else:
                logger.info(f"    {var_name} [{desc}]: 全部 NaN")


    # =========================================================================
    # 步骤 7i: Janis-Fadner (J-F) 情绪系数 — 稳健性替代指标
    # 学术依据: Janis & Fadner (1965); Deephouse (2000, SMJ)
    # 公式:
    #   若 P > N: JF = (P² - P×N) / (P+N)²
    #   若 N > P: JF = (P×N - N²) / (P+N)²
    #   若 P = N: JF = 0
    # 取值范围: [-1, +1], 克服简单均值的零分悖论
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7i: Janis-Fadner (J-F) 情绪系数")
    logger.info("=" * 60)

    for track in ['_full', '_ctx', '_title']:
        pos_col = f'pos_count{track}'
        neg_col = f'neg_count{track}'
        if pos_col in panel.columns and neg_col in panel.columns:
            P = panel[pos_col].fillna(0)
            N = panel[neg_col].fillna(0)
            total_sq = (P + N) ** 2
            # 安全除法: 防止 0/0
            safe_denom = total_sq.replace(0, np.nan)

            jf = np.where(
                P > N,
                (P**2 - P * N) / safe_denom,
                np.where(
                    N > P,
                    (P * N - N**2) / safe_denom,
                    0.0  # P == N
                )
            )
            panel[f'jf_coefficient{track}'] = np.where(
                safe_denom.isna(), np.nan, jf
            )
            logger.info(f"  jf_coefficient{track}: "
                        f"mean={panel[f'jf_coefficient{track}'].mean():.4f}, "
                        f"std={panel[f'jf_coefficient{track}'].std():.4f}")
        else:
            logger.warning(f"  {pos_col} 或 {neg_col} 不存在, 跳过 J-F 系数{track}")

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

    logger.info("45_panel_export_main 执行完毕 ✓")


if __name__ == '__main__':
    main()
