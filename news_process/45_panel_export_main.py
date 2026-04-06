"""
45_panel_export_main.py — 面板导出与主流程编排 (入口文件)
==========================================================

功能:
  - 面板诊断统计 (log_diagnostics)
  - 多格式导出: Parquet + Stata .dta (export_panel)
  - 主流程编排 main(): 41→42→43→44→45 的执行序列

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
_p42 = os.path.join(os.path.dirname(__file__), '42_panel_attention_media.py')
_s42 = _iu.spec_from_file_location('_42_mod', _p42)
_m42 = _iu.module_from_spec(_s42)
_s42.loader.exec_module(_m42)

compute_fintech_attention_index = _m42.compute_fintech_attention_index
compute_media_heterogeneity = _m42.compute_media_heterogeneity

# --- 从 43 导入 ---
_p43 = os.path.join(os.path.dirname(__file__), '43_panel_indicators_geography.py')
_s43 = _iu.spec_from_file_location('_43_mod', _p43)
_m43 = _iu.module_from_spec(_s43)
_s43.loader.exec_module(_m43)

compute_composite_indicators = _m43.compute_composite_indicators
standardize_panel_variables = _m43.standardize_panel_variables
merge_bank_geography = _m43.merge_bank_geography
compute_leave_one_out_sentiment = _m43.compute_leave_one_out_sentiment

# --- 从 44 导入 ---
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
                # Bartik IV — 媒体省份 (稳健性 7)
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

    # --- 3c. 媒体权威性加权列预计算 (Holzman et al. 2023, TAR) ---
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
            for track in ['_full', '_ctx']:
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
        for track in ['_full', '_ctx']:
            src_col = f'bartik_type_iv{track}'
            ptmp = ptmp.rename(columns={src_col: f'bartik_type_iv{track}_t01'})
        panel = panel.merge(
            ptmp[['target_bank', 'year',
                  'bartik_type_iv_full_t01',
                  'bartik_type_iv_ctx_t01']],
            on=['target_bank', 'year'], how='left')

        # --- 稳健性 1: 银行规模 (4类, 3有效IV) ---
        panel = compute_bartik_iv(panel, df_exploded, scale_map, 'scale')

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

        # --- 稳健性 10: 半年度 ---
        date_col = '日期'
        if date_col in df_exploded.columns:
            df_exploded['_half_year'] = df_exploded[date_col].apply(
                lambda x: 'H1' if pd.to_datetime(x).month <= 6 else 'H2'
            )
            half_map = {'H1': 'H1', 'H2': 'H2'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, half_map, 'half',
                category_col='_half_year'
            )
        else:
            logger.warning(f"  列 '{date_col}' 不存在, 跳过半年度 Bartik")

        # --- 稳健性 11: 季度 ---
        if date_col in df_exploded.columns:
            df_exploded['_quarter'] = df_exploded[date_col].apply(
                lambda x: f'Q{(pd.to_datetime(x).month - 1) // 3 + 1}'
            )
            qtr_map = {'Q1': 'Q1', 'Q2': 'Q2', 'Q3': 'Q3', 'Q4': 'Q4'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, qtr_map, 'qtr',
                category_col='_quarter'
            )

        # --- 稳健性 12: 月度 ---
        if date_col in df_exploded.columns:
            df_exploded['_pub_month'] = df_exploded[date_col].apply(
                lambda x: f'M{pd.to_datetime(x).month:02d}'
            )
            month_map = {f'M{m:02d}': f'M{m:02d}' for m in range(1, 13)}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, month_map, 'month',
                category_col='_pub_month'
            )

        # --- 稳健性 13: 工作日/周末 ---
        if date_col in df_exploded.columns:
            df_exploded['_wkday_type'] = df_exploded[date_col].apply(
                lambda x: 'weekend' if pd.to_datetime(x).dayofweek >= 5 else 'weekday'
            )
            wkday_map = {'weekday': 'weekday', 'weekend': 'weekend'}
            panel = compute_bartik_iv_fintech(
                panel, df_exploded, wkday_map, 'wkday',
                category_col='_wkday_type'
            )

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
