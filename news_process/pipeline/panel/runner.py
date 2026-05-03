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

import numpy as np
import pandas as pd

# Phase 2a: 全部 9 处 importlib.spec_from_file_location 反射已删除,
# 改为正规子包 import (单源真值: news_process.pipeline.panel.encode 取代 41 号文件)。
from news_process.pipeline.panel.encode import (
    CONFIG, STAGE_NAME, logger, OUTPUT_DIR, FILENAMES, PANEL_CFG,
    LLM_MODELS, DICT_NAMES, BERT_MODELS, THREE_CLASS_MODELS, SENTIMENT_MAP,
    encode_sentiment, compute_media_authority_weights, parse_time,
    build_aggregation_dict, aggregate_panel, balance_panel,
)
from utils.helpers import log_stage_summary, save_dataset

# 从 panel.attention_media (原 42)
from news_process.pipeline.panel.attention_media import (
    compute_fintech_attention_index, compute_media_heterogeneity,
)

# 从 panel.geography (原 43)
from news_process.pipeline.panel.geography import (
    compute_composite_indicators, standardize_panel_variables,
    merge_bank_geography, compute_leave_one_out_sentiment,
)

# 从 panel.iv_did (原 44)
from news_process.pipeline.panel.iv_did import (
    load_bank_group_maps, compute_bartik_iv, compute_bartik_iv_fintech,
    PROVINCE_TO_ZONE, compute_zone_leave1out, merge_policy_shocks,
)

# 从 panel.network_spillover (原 46) — getattr 守护可选符号
from news_process.pipeline.panel import network_spillover as _ns
compute_network_spillovers = getattr(_ns, 'compute_network_spillovers', None)
compute_bank_network_centrality = getattr(_ns, 'compute_bank_network_centrality', None)
compute_cognitive_proximity = getattr(_ns, 'compute_cognitive_proximity', None)
compute_embedding_peer_network = getattr(_ns, 'compute_embedding_peer_network', None)
del _ns

# 从 panel.network_brokerage (原 47)
from news_process.pipeline.panel import network_brokerage as _nb
compute_brokerage_centrality = getattr(_nb, 'compute_brokerage_centrality', None)
compute_industry_neg_shock = getattr(_nb, 'compute_industry_neg_shock', None)
compute_fire_sale_interaction = getattr(_nb, 'compute_fire_sale_interaction', None)
del _nb

# 从 panel.llm_peer_iv (原 48)
from news_process.pipeline.panel import llm_peer_iv as _lp
compute_llm_peer_iv = getattr(_lp, 'compute_llm_peer_iv', None)
del _lp

# 从 features.strategic_diff (原 25)
from news_process.pipeline.features import strategic_diff as _sd
compute_strategic_differentiation = getattr(
    _sd, 'compute_strategic_differentiation', None)
del _sd

# 从 features.policy_similarity (原 26)
from news_process.pipeline.features import policy_similarity as _ps
compute_authoritative_similarity = getattr(
    _ps, 'compute_authoritative_similarity', None)
del _ps

# 从 features.benefit_society (原 27)
from news_process.pipeline.features import benefit_society as _bs
compute_benefit_society_panel = getattr(
    _bs, 'compute_benefit_society_panel', None)
del _bs



# ============================================================================
# 8 + 9. Diagnostics + Export — extracted to export.py in Phase 2b for
# single-responsibility separation.  Re-exported here for backwards compat.
# ============================================================================
from news_process.pipeline.panel.export import log_diagnostics, export_panel  # noqa: E402,F401



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
            # Logit-to-Score 概率分数
            src_prob = f'llm_prob_score{track}'
            if src_prob in df.columns:
                df[f'llm_prob_score_w{track}'] = df[src_prob] * w
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
            # Logit-to-Score 概率分数
            src_prob = f'llm_prob_score{track}'
            if src_prob in df.columns:
                df[f'llm_prob_score_mw{track}'] = df[src_prob] * mw
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
            # Logit-to-Score 概率分数
            src_prob = f'llm_prob_score{track}'
            if src_prob in df.columns:
                df[f'llm_prob_score_hw{track}'] = df[src_prob] * hw
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
    # 构造 40 种洗稿率变体 (10 方法 × 双轨 Full/Ctx) 的篇章级标记列:
    #   A:  LLM 多数投票 (is_positive{track}, 双轨)
    #   A2: 单个 LLM (逐 LLM 情感{track} > 0)
    #   B:  反向验证 (负面{track} ∧ 实质性)
    #   D/D2: 词典均值 / 单词典 ({dict}_score{track} > 0)
    #   E/E2: BERT 均值 / 单 BERT ({bert}_正面{track} > 0.5)
    #   F:  高置信度子样本 (agreement_rate{track} ≥ 2/3)
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
                # negative 编码 (Garcia 2013, JF → disag 输入)
                df[f'_is_{llm}_negative{track}'] = (df[src_col] < 0).astype(int)

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
                # negative 编码 (Garcia 2013, JF → disag 输入)
                df[f'_is_{d}_negative{track}'] = (df[src_col] < 0).astype(int)

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
                # negative 编码 (Garcia 2013, JF → disag 输入)
                neg_src = f'{b}_负面{track}'
                if neg_src in df.columns:
                    df[f'_is_{b}_negative{track}'] = (df[neg_src] > 0.5).astype(int)

        # --- 方法 F: 高置信度子样本 (Shapiro et al. 2022, JoE) ---
        agr_col = f'llm_agreement_rate{track}'
        if agr_col in df.columns:
            _hc = df[agr_col].fillna(0) >= 0.67
            df[f'_is_pos_hc{track}'] = ((df[pos_col] == 1) & _hc).astype(int)
            df[f'_is_pos_desc_hc{track}'] = (
                (df[pos_col] == 1) & _is_desc & _hc
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
        # Phase 1 重构: 优先读取 CONFIG['paths']['media_classification_file']。
        cls_path = CONFIG['paths'].get(
            'media_classification_file',
            os.path.join(os.path.dirname(__file__),
                         'config', 'media_classification.json'),
        )
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
        # Phase 1 重构: 优先读取 CONFIG['paths']['media_weights_file']。
        mw_path = CONFIG['paths'].get(
            'media_weights_file',
            os.path.join(os.path.dirname(__file__),
                         'config', 'media_weights.json'),
        )
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
            # Phase 1 重构: 优先读取 CONFIG['paths']['bank_addresses_file']。
            addr_path = CONFIG['paths'].get(
                'bank_addresses_file',
                os.path.join(os.path.dirname(__file__),
                             'config', 'bank_addresses.json'),
            )
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

    # --- 7h-strat. 战略差异度指数 (Guzman & Li 2023; Hoberg & Phillips 2016) ---
    if compute_strategic_differentiation is not None:
        panel = compute_strategic_differentiation(df_exploded, panel)
    else:
        logger.info("  compute_strategic_differentiation 不可用, 跳过")

    # --- 7h-auth. 权威政策战略响应度 (Hassan et al. 2019, QJE) ---
    if compute_authoritative_similarity is not None:
        panel = compute_authoritative_similarity(df_exploded, panel)
        # 【学术防塌陷熔断机制 (Mathematical & Academic Fallback)】
        # 补全可能由于分轨导致部分银行在某一轨中没有数据而产生的 NaN 为 0.0。
        # 学术合理性：在 NLP 向量空间中，如果没有观测到该维度的新闻（例如银行该年度无 Ctx 语境文本），
        # 那么其特征向量为空 (zero-vector)。由于余弦相似度的定义为内积，零向量与政策锚点向量的相似度
        # 在数学上严格正交且为 0.0。因此，此处使用 0.0 填充不仅是为了保证 STATA 面板的严格平衡性，
        # 更是理论层面的必然要求，彻底避免了因 NaN 导致观测样本丢失 (Listwise Deletion) 的计量学灾难。
        sim_cols = [c for c in panel.columns if c.startswith('auth_sim_')]
        if sim_cols:
            panel[sim_cols] = panel[sim_cols].fillna(0.0)
    else:
        logger.info("  compute_authoritative_similarity 不可用, 跳过")

    # --- 7h-benefit. 经营效益情感态度投影 (Jha, Liu & Manela 2026, RFS) ---
    # 【学术依据】Jha et al. (2026, RFS §1.3.2 Eq. 1): 双极连续余弦投影
    #   a_j = cos(s_j, mean(pos) - mean(neg))
    # 【白话】用"利好经营 vs 损害经营"方向轴给每篇新闻打态度分
    if compute_benefit_society_panel is not None:
        panel = compute_benefit_society_panel(panel, df_exploded)
        # 【学术防塌陷熔断机制】
        # 零向量投影 = 中性 (cos(0, p) = 0)，NaN → 0.0 保证面板严格平衡
        bene_cols = [c for c in panel.columns if c.startswith('benefit_')]
        if bene_cols:
            panel[bene_cols] = panel[bene_cols].fillna(0.0)
    else:
        logger.info("  compute_benefit_society_panel 不可用, 跳过")

    # --- 7h-token. 文章级政策对齐 + Token/Hidden 四象限分类 ---
    # 【学术支撑】
    #   Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to
    #   impact. Research Policy, 55(3), 105426.
    #   https://doi.org/10.1016/j.respol.2026.105426
    #   -> S3.2.1: 解耦"显性引用"(Token) 与"文本级语义实质借鉴"(Hidden)
    #
    #   Westphal, J. D. & Zajac, E. J. (2001). Decoupling policy from practice.
    #   ASQ, 46(2), 202-228. https://doi.org/10.2307/2667086
    #   -> Token Adoption = 象征性采用 (合法性功能)
    #
    # 【白话说明】
    #   读取 Stage 15 的逐篇文章政策对齐分数 (policy_cosine_sim),
    #   结合词频维度(双轨), 把每篇文章分到四个象限:
    #     Token(说得多+没落地) / Hidden(说得少+做得真) /
    #     Substantive(言行一致) / Irrelevant(不相关)
    #   然后按(银行,年)统计各象限的文章占比, 作为面板变量.
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("步骤 7h-token: 文章级政策对齐 + Token/Hidden 四象限分类")
    logger.info("=" * 60)

    # 尝试加载 Stage 15 输出
    _align_filename = FILENAMES.get(
        'output_15_article_alignment', '15_article_alignment.parquet')
    _align_path = os.path.join(OUTPUT_DIR, _align_filename)

    if os.path.exists(_align_path):
        df_align = pd.read_parquet(_align_path)
        logger.info(f"  加载 Stage 15: {len(df_align)} 篇, "
                    f"policy_cosine_sim 非空率: "
                    f"{df_align['policy_cosine_sim'].notna().mean():.1%}")

        # 【关键】Stage 15 的输出基于 Stage 14 (14_fintech_intensity.parquet),
        #   该文件不含 'year' 列 — year 由 Stage 45 的 parse_time() 从 '日期' 派生。
        #   因此必须在此处自行从 '日期' 列计算 year, 否则 groupby('year') 会 KeyError。
        if 'year' not in df_align.columns and '日期' in df_align.columns:
            df_align['日期'] = pd.to_datetime(df_align['日期'], errors='coerce')
            df_align['year'] = df_align['日期'].dt.year
            df_align = df_align.dropna(subset=['year'])
            df_align['year'] = df_align['year'].astype(int)
            logger.info(f"  从 '日期' 列派生 year: {df_align['year'].nunique()} 个年份")

        # --- 逻辑 A: 连续聚合变量 (主回归) ---
        # 【术语】按 (target_bank, year) 聚合文章级 policy_cosine_sim
        #   为 mean 和 std, 以及 fintech_intensity_score 的 mean
        #   参考: Royston, Altman & Sauerbrei (2006, Stat Med) --
        #   连续变量优于离散化
        # 【白话】算每家银行每年的平均政策对齐分和平均技术强度分
        if 'target_bank' in df_align.columns and 'year' in df_align.columns:
            _agg = df_align.groupby(['target_bank', 'year']).agg(
                article_sim_mean=('policy_cosine_sim', 'mean'),
                article_sim_std=('policy_cosine_sim', 'std'),
                fintech_intensity_mean=('fintech_intensity_score', 'mean')
            ).reset_index()
            # std 对单篇文章的 bank-year 返回 NaN, 填 0
            _agg['article_sim_std'] = _agg['article_sim_std'].fillna(0.0)
            panel = panel.merge(_agg, on=['target_bank', 'year'], how='left')
            logger.info(f"  连续聚合: article_sim_mean/std, "
                        f"fintech_intensity_mean 已合并")

            # --- 逻辑 B: 四象限离散分类 (机制检验 / 稳健性) ---
            # 【术语】
            #   双轨词频维度:
            #     Track A (kw): fintech_distinct_keywords (AC 原始去重关键词数)
            #     Track B (int): fintech_intensity_score (TF-IDF x SIF 加权)
            #   分位数阈值: P={25, 50, 75}
            #     P50 = 机制检验基准 (与项目 10+ 处中位数分割惯例一致)
            #     P25/P75 = 稳健性检验
            #
            #   四象限定义 (逐篇文章级):
            #     Substantive: 词频 >= 分位数 AND 相似度 >= 分位数 (言行一致)
            #     Token:       词频 >= 分位数 AND 相似度 <  分位数 (洗科技)
            #     Hidden:      词频 <  分位数 AND 相似度 >= 分位数 (闷声干大事)
            #     Irrelevant:  词频 <  分位数 AND 相似度 <  分位数 (不相关)
            #
            # 【白话】把每篇新闻放进四个格子里:
            #   纵轴 = 关键词多不多, 横轴 = 跟政策像不像
            #   然后数每家银行每年各有多少比例的新闻在每个格子里

            _tracks = [
                ('kw', 'fintech_distinct_keywords'),
                ('int', 'fintech_intensity_score'),
            ]
            _align_cfg = CONFIG.get('article_alignment', {})
            _percentiles = _align_cfg.get('quadrant_percentiles', [25, 50, 75])

            for track_name, freq_col in _tracks:
                if freq_col not in df_align.columns:
                    logger.warning(f"  {freq_col} 列缺失, 跳过 Track {track_name}")
                    continue

                for pct in _percentiles:
                    # 按年度计算分位数阈值
                    # 使用默认参数绑定 p=pct, 防止 late-binding 陷阱
                    _yearly_sim_thresh = df_align.groupby('year')[
                        'policy_cosine_sim'].transform(
                        lambda x, p=pct: x.quantile(p / 100.0))
                    _yearly_freq_thresh = df_align.groupby('year')[
                        freq_col].transform(
                        lambda x, p=pct: x.quantile(p / 100.0))

                    # 四象限分类 (互斥穷尽)
                    _high_freq = df_align[freq_col] >= _yearly_freq_thresh
                    _high_sim = df_align['policy_cosine_sim'] >= _yearly_sim_thresh

                    df_align[f'_is_token_{track_name}_p{pct}'] = (
                        _high_freq & ~_high_sim).astype(int)
                    df_align[f'_is_hidden_{track_name}_p{pct}'] = (
                        ~_high_freq & _high_sim).astype(int)
                    df_align[f'_is_subst_{track_name}_p{pct}'] = (
                        _high_freq & _high_sim).astype(int)

                    # 按 (银行, 年) 聚合为占比
                    _quadrant_agg = df_align.groupby(
                        ['target_bank', 'year']).agg(
                        **{f'token_adopt_{track_name}_p{pct}': (
                            f'_is_token_{track_name}_p{pct}', 'mean'),
                           f'hidden_adopt_{track_name}_p{pct}': (
                            f'_is_hidden_{track_name}_p{pct}', 'mean'),
                           f'subst_adopt_{track_name}_p{pct}': (
                            f'_is_subst_{track_name}_p{pct}', 'mean'),
                           }
                    ).reset_index()

                    panel = panel.merge(
                        _quadrant_agg, on=['target_bank', 'year'], how='left')

                logger.info(f"  Track {track_name}: P={{25,50,75}} "
                            f"四象限占比已合并")

            # 填充 NaN (无 Stage 15 数据的 bank-year)
            _token_cols = [c for c in panel.columns
                          if c.startswith(('token_adopt_', 'hidden_adopt_',
                                           'subst_adopt_', 'article_sim_',
                                           'fintech_intensity_mean'))]
            panel[_token_cols] = panel[_token_cols].fillna(0.0)
            logger.info(f"  Token/Hidden 面板变量: 共 {len(_token_cols)} 列")

            # 清理临时列
            _tmp_cols = [c for c in df_align.columns if c.startswith('_is_')]
            df_align.drop(columns=_tmp_cols, inplace=True, errors='ignore')

        else:
            logger.warning("  Stage 15 数据缺少 target_bank/year 列, 跳过")
    else:
        logger.info(f"  Stage 15 文件不存在 ({_align_path}), 跳过 Token/Hidden 计算")

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

    # --- 7h-emb. Embedding 同业网络控制 (Hoberg & Phillips 2016; Reimers 2019) ---
    # 基于 Sentence Embedding 向量相似度构建动态同业网络权重矩阵,
    # 计算加权同行情感作为控制变量, 补充共现网络的语义维度。
    if compute_embedding_peer_network is not None:
        panel = compute_embedding_peer_network(df_exploded, panel)
    else:
        logger.info("  compute_embedding_peer_network 不可用, 跳过")

    # --- 7h-llmpeer. LLM-Peer 动态竞争网络 IV (Cao et al. 2025) ---
    # 基于 LLM 语义判断构建竞争同行网络, 加权同行情感作为 IV。
    # 双重筛选句子 (2+ 银行名 + 金融科技关键词) → GPT → 模糊匹配 → 滞后 IV
    if compute_llm_peer_iv is not None:
        panel = compute_llm_peer_iv(panel, df_exploded)
    else:
        logger.info("  compute_llm_peer_iv 不可用, 跳过")

    # =========================================================================
    # 步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 双轨构造
    # =========================================================================
    # 学术依据:
    #   Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022).
    #   Cheap talk and cherry-picking. Finance Research Letters, 47(B), 102776.
    #   https://doi.org/10.1016/j.frl.2022.102776
    #
    # 构造 40 种洗稿率变体 (10 方法 × 双轨 Full/Ctx):
    #   A/A2: LLM 投票 + 单 LLM (3模型) × 双轨
    #   B:    反向验证 + 非对称性 × 双轨
    #   C:    情感纯度缺口 × 双轨
    #   D/D2: 词典均值 + 单词典 (5本) × 双轨
    #   E/E2: BERT 均值 + 单 BERT (5模型) × 双轨
    #   F:    高置信度子样本 × 双轨
    #   G:    描述性文章情感偏移 × 双轨
    # =========================================================================
    logger.info("=" * 60)
    logger.info("步骤 7h: 洗稿率 (Washing Ratio) — 多方法 × 双轨构造 (40种)")
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

        # --- 方法 C: 情感纯度缺口 (实质性 vs 描述性) ---
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

    # ═══ 8b. 情感意见分歧 (Disagreement Index) ═══
    # 姜富伟, 李梦如, 孟令超 (2024). 调预期、防风险：央行金融稳定沟通效果研究.
    #   经济学（季刊）, 24(6), 2281-2300. DOI: 10.13821/j.cnki.ceq.2024.06.19
    # Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise?
    #   The Journal of Finance, 59(3), 1259-1294. DOI: 10.1111/j.1540-6261.2004.00662.x
    # 公式: disag = sqrt(1 - ((pos - neg) / (pos + neg))²)  ∈ [0, 1]
    #   0 = 完全一致 (全正或全负), 1 = 最大分歧 (正负相等)
    def _compute_disag(p_col, n_col, _panel):
        """通用 disag 计算, 处理 denom=0 边界 → NaN"""
        if p_col not in _panel.columns or n_col not in _panel.columns:
            return pd.Series(np.nan, index=_panel.index)
        p, n = _panel[p_col], _panel[n_col]
        denom = p + n
        ratio = ((p - n) / denom.replace(0, np.nan)) ** 2
        return np.sqrt(1 - ratio)

    for track in ['_full', '_ctx']:
        # (a) 词典综合 (词级比率)
        panel[f'disag{track}'] = _compute_disag(
            f'avg_pos_ratio{track}', f'avg_neg_ratio{track}', panel)
        # (b) 单词典 (词级比率)
        for d in DICT_NAMES:
            panel[f'disag_{d}{track}'] = _compute_disag(
                f'avg_{d}_pos_ratio{track}', f'avg_{d}_neg_ratio{track}', panel)
        # (c) LLM 投票综合 (篇章计数)
        panel[f'disag_llm{track}'] = _compute_disag(
            f'pos_count{track}', f'neg_count{track}', panel)
        # (d) 单 LLM (篇章计数)
        for llm in LLM_MODELS:
            panel[f'disag_{llm}{track}'] = _compute_disag(
                f'{llm}_pos_count{track}', f'{llm}_neg_count{track}', panel)
        # (e) BERT 综合 (概率均值, 43 L86 生成)
        panel[f'disag_bert{track}'] = _compute_disag(
            f'bert_avg_pos{track}', f'bert_avg_neg{track}', panel)
        # (f) 单 BERT (概率均值)
        for b in BERT_MODELS:
            panel[f'disag_{b}{track}'] = _compute_disag(
                f'{b}_pos{track}', f'{b}_neg{track}', panel)
    logger.info(f"  disag 指标计算完成 (32 变量)")

    # ═══ 8c. 对数降噪定向情感 (Log-Transformed Sentiment) ═══
    # Angelico, C., Marcucci, J., Miccoli, M., & Quarta, F. (2022).
    #   Can we measure inflation expectations using Twitter?
    #   Journal of Econometrics, 228(2), 259-277. DOI: 10.1016/j.jeconom.2021.12.008
    # 公式: log_sent = log(1 + pos_count) - log(1 + neg_count)
    for track in ['_full', '_ctx']:
        pc, nc = f'pos_count{track}', f'neg_count{track}'
        if pc in panel.columns and nc in panel.columns:
            panel[f'log_sent{track}'] = (
                np.log1p(panel[pc].fillna(0)) -
                np.log1p(panel[nc].fillna(0)))
    logger.info(f"  log_sent 指标计算完成 (2 变量)")

    # ═══ 8d. 算法迎合度 (Algorithmic Catering) — 全展开 ═══
    # Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk
    #   when a machine is listening. RFS, 36(9), 3603-3642. DOI: 10.1093/rfs/hhad021
    # Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT.
    #   CAR, 40(2), 806-841. DOI: 10.1111/1911-3846.12832
    # 公式: algo_cater = dict_tone - deep_model_tone
    #   正值 → 词典比深层模型更正面 (潜在迎合)
    _cater_count = 0
    for track in ['_full', '_ctx']:
        dc = f'dict_avg_tone{track}'
        lc = f'llm_vote_tone{track}'
        bp, bn = f'bert_avg_pos{track}', f'bert_avg_neg{track}'

        # A. 综合词典 vs 综合 LLM
        if dc in panel.columns and lc in panel.columns:
            panel[f'algo_cater{track}'] = panel[dc] - panel[lc]
            _cater_count += 1
        # A2. 综合词典 vs 综合 BERT
        if dc in panel.columns and bp in panel.columns and bn in panel.columns:
            panel[f'algo_cater_b{track}'] = panel[dc] - (panel[bp] - panel[bn])
            _cater_count += 1

        # B. 单词典 vs 综合深层模型
        for d in DICT_NAMES:
            d_col = f'{d}_tone{track}'
            if d_col in panel.columns:
                if lc in panel.columns:
                    panel[f'{d}_cater{track}'] = panel[d_col] - panel[lc]
                    _cater_count += 1
                if bp in panel.columns and bn in panel.columns:
                    panel[f'{d}_cater_b{track}'] = panel[d_col] - (panel[bp] - panel[bn])
                    _cater_count += 1

        # C. 综合词典 vs 单深层模型
        if dc in panel.columns:
            for llm in LLM_MODELS:
                llm_s = f'{llm}_tone{track}'
                if llm_s in panel.columns:
                    panel[f'cater_{llm}{track}'] = panel[dc] - panel[llm_s]
                    _cater_count += 1
            for b in BERT_MODELS:
                b_p, b_n = f'{b}_pos{track}', f'{b}_neg{track}'
                if b_p in panel.columns and b_n in panel.columns:
                    panel[f'cater_{b}{track}'] = panel[dc] - (panel[b_p] - panel[b_n])
                    _cater_count += 1
    logger.info(f"  algo_cater 指标计算完成 ({_cater_count} 变量)")

    # ═══ 8e. 数据双轨 (Data Dual-Track) 稳健性特征融合 (Stage 30) ═══
    # 【学术机制】稳健性联合检验 (Robustness Joint Testing)
    # 通过将本地特征矩阵与面板数据合并，应对大语言模型潜在的“幻觉偏移”(Hallucination Bias)。
    t2v_path = os.path.join(OUTPUT_DIR, '30_text2vec_indicators.parquet')
    if os.path.exists(t2v_path):
        logger.info(f"  合并 30_text2vec_indicators.parquet...")
        t2v_df = pd.read_parquet(t2v_path)
        panel = panel.merge(t2v_df, on=['target_bank', 'year'], how='left')
        
        # 正交保护 (Orthogonal Protection): 拒绝 0.0 填充
        # 【学术机制】Listwise Deletion vs Sample Selection Bias
        # 理论基石：Allison, P. D. (2001). Missing Data. SAGE Publications. DOI: 10.4135/9781412985079
        # Heckman, J. J. (1979). Sample Selection Bias as a Specification Error. Econometrica, 47(1), 153-161. DOI: 10.2307/1912352
        # 修正：此前试图对无新闻样本使用 0.0 补偿，但这在计量经济学上是致命的。
        # 0.0 距离代表该银行完美贴合行业均值质心，0.0 相似度代表绝对正交。
        # 强制将“无数据”转化为极端的“0值”，会导致 TWFE 回归中出现大量人造的人工断点 (Artificial Spikes)，
        # 严重扭曲真实系数。因此，必须保留 NaN，交由 Stata 在固定效应面板回归中自动执行 Listwise Deletion，
        # 维护样本空间的连续性，避免人为制造的伪稳健性。
        # 【通俗应用】如果一家银行整年连一条新闻都没有，我们不能强行说它“和大家完全一样”或者“完全相反”，
        # 最科学的做法就是留空 (NaN)，让 Stata 在跑回归的时候自动忽略没有数据的那几年，避免假数据捣乱。
        t2v_cols = [
            'strat_diff_t2v_full', 'strat_diff_t2v_ctx',
            'policy_cosine_sim_t2v_full', 'policy_cosine_sim_t2v_ctx'
        ]
        logger.info(f"  ✅ 成功挂载双轨稳健性特征 (保留自然缺失值 NaN): {t2v_cols}")
    else:
        logger.warning(f"  ⚠️ 未找到 {t2v_path}，跳过双轨特征挂载。")

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
